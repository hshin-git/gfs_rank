###########################################
## GFSファイルからCSVファイルを作成
###########################################
import numpy as np
import pandas as pd
import os,sys,shutil
#import matplotlib.pyplot as plt
from datetime import datetime,timedelta

import netCDF4
from netCDF4 import num2date

import COMMON as COM


###########################################
print("enter:", sys.argv)
print(sys.argv[0], datetime.now())

## 引数の数により動作モードをスイッチ（予測か統計か）
FORECAST = True if len(sys.argv) < 3 else False

## コマンドライン引数: 開始日、終了日、ステップ
JST1 = datetime.now()
JST1 = datetime.strptime(sys.argv[1][:8],"%Y%m%d") if len(sys.argv) > 1 else datetime(JST1.year,JST1.month,JST1.day,0)

JST2 = JST1 + timedelta(days=7)
JST2 = datetime.strptime(sys.argv[2][:8],"%Y%m%d") + timedelta(days=1) if len(sys.argv) > 2 else JST2

STEP = 1
STEP = int(sys.argv[3]) if len(sys.argv) > 3 else STEP

## 動作モードにより出力先をスイッチ
#OUT_PATH = "./forecast" if FORECAST else "./hindcast"
OUT_PATH = COM.FCST_PATH if FORECAST else COM.HCST_PATH
os.makedirs(OUT_PATH, exist_ok=True)


###########################################
## GFSファイルの列挙
DAYS = (JST2-JST1).days
TIME_NAME = "JST"
TIME_ZONE = 9
UTC1 = JST1 - timedelta(hours=TIME_ZONE)
UTC2 = JST2 - timedelta(hours=TIME_ZONE)

GFS_INIT = 12
GFS_DAYS = 7
GFS_PATH = []
GFS_ROOT = "./gfs"
for d in range(0,DAYS,STEP):
  UTC = UTC1 + timedelta(days=d)
  GFS = GFS_ROOT +"/"+ "gfs_%s%02d_%03d.nc"%(UTC.strftime("%Y%m%d"),GFS_INIT,24*GFS_DAYS)
  if os.path.exists(GFS): GFS_PATH += [GFS]

##
print(sys.argv[0], JST1)
print(sys.argv[0], JST2)
print(sys.argv[0], GFS_PATH)
print(sys.argv[0], OUT_PATH)
#sys.exit(0)

###########################################
def lat_lon_to_y_x(lat,lon,lat_,lon_):
  y = np.argmin(np.abs(lat-lat_))
  x = np.argmin(np.abs(lon-lon_))
  return y,x

###########################################
## 抽出地点と気象変数の指定
ENCODE = "cp932"
SDP_LIST = pd.read_csv(COM.INFO_PATH +"/"+ "sdp_list.csv", index_col="SDP",encoding=ENCODE)
GFS_LIST = pd.read_csv(COM.INFO_PATH +"/"+ "gfs_list.csv", index_col="GFS",encoding=ENCODE)
VAR_LIST = GFS_LIST[(GFS_LIST.LAYERS>=1)&(GFS_LIST.LAYERS<10)].index.tolist()
"""
# デバッグ用: 地点と変数を制限
SDP_LIST = SDP_LIST[:4]
VAR_LIST = ['Temperature_surface']
"""

## GFS抽出データの格納先
GFS_DATA = {}
for SDP in SDP_LIST.index: GFS_DATA[SDP] = []

for GFS in GFS_PATH:
  ###########################################
  ## GFSファイルの参照開始
  data =  netCDF4.Dataset(GFS, 'r')
  ## 緯度、経度から配列添字へ
  LAT_ = np.array(data["lat"][:].squeeze())
  LON_ = np.array(data["lon"][:].squeeze())
  ###########################################
  # 抽出地点のループ
  for SDP in SDP_LIST.index[:]:
    NAME = SDP_LIST.loc[SDP,"NAME"]
    LAT = SDP_LIST.loc[SDP,"lat"]
    LON = SDP_LIST.loc[SDP,"lon"]
    y,x = lat_lon_to_y_x(LAT,LON,LAT_,LON_)
    print(sys.argv[0], "%05d %d %d %.3f %.3f %s"%(SDP,y,x,LAT,LON,NAME))

    ###########################################
    # CSV用データフレームの作成
    time_var = data.variables['time']
    time_vals = num2date(time_var[:].squeeze(), time_var.units)

    reftime_var = data.variables['reftime']
    reftime_vals = num2date(reftime_var[:].squeeze(), reftime_var.units)

    START = time_vals[0].strftime("%Y%m%d %H:%M")
    END = time_vals[-1].strftime("%Y%m%d %H:%M")
    FREQ = "%dH" % int((time_vals[1] - time_vals[0]).seconds/3600)

    INDEX = pd.date_range(START, END, freq=FREQ)
    DATAF = pd.DataFrame(index=INDEX)
    DATAF.index = DATAF.index + timedelta(hours=TIME_ZONE)
    DATAF.index.name = TIME_NAME

    DATAF["reftime"] = reftime_vals

    ## 気象変数のループ
    for NAME in VAR_LIST:
      data_vals = data.variables[NAME][:].squeeze()
      SHAPE = data_vals.shape
      DIM = len(SHAPE)
      NZ = 1 if DIM==3 else SHAPE[1]
      NT = len(INDEX)
      ## 高さ方向のループ
      for z in range(0,NZ):
        c = "%s_%02d"%(NAME,z)
        if SHAPE[0]!=NT:
          print(sys.argv[0], "skip",NAME)
          DATAF[c] = np.nan
        elif DIM==3:
          DATAF[c] = data_vals[:,y,x]
        elif DIM==4:
          DATAF[c] = data_vals[:,z,y,x]

    ###########################################
    ## CSVファイルの保存
    GFS_DATA[SDP] += [DATAF]

  ###########################################
  ## GFSファイルの参照終了
  data.close()

###########################################
PERCENTILES = np.linspace(0.01,0.99,99)
MEAN_3H = []
MEAN_1D = []
for SDP in SDP_LIST.index:
  print(sys.argv[0], SDP,"concat and save ...")
  ## データフレームを結合
  DATA = pd.concat(GFS_DATA[SDP])
  ## 時刻の重複を除去
  DATA[TIME_NAME] = DATA.index
  DATA = DATA.drop_duplicates(subset=TIME_NAME,keep='last')
  DATA = DATA.drop(columns=TIME_NAME)
  ## 指定期間のデータフレームへ
  TEMP = pd.DataFrame(index=pd.date_range(JST1,JST2,freq=FREQ))
  TEMP.index.name = 'JST'
  DATA = TEMP.join(DATA)
  ## 統計値の計算
  STAT = DATA.describe(percentiles=PERCENTILES)
  MEAN_3H += [DATA.resample("3H").mean()]
  MEAN_1D += [DATA.resample("1D").mean()]
  ## ファイルの保存
  if FORECAST:
    DATA.to_csv(OUT_PATH +"/"+ "%05d.csv"%SDP)
  else:
    DATA.to_csv(OUT_PATH +"/"+ "%05d.csv"%SDP)
    STAT.to_csv(OUT_PATH +"/"+ "%05d_stat.csv"%SDP)

###########################################
GFS_MEAN3H = pd.concat(MEAN_3H).describe(percentiles=PERCENTILES)
GFS_MEAN1D = pd.concat(MEAN_1D).describe(percentiles=PERCENTILES)
GFS_MEAN3H.to_csv(OUT_PATH +"/"+ "gfs_mean3h.csv")
GFS_MEAN1D.to_csv(OUT_PATH +"/"+ "gfs_mean1d.csv")

##################################################
print("leave:", sys.argv)
sys.exit(0)

