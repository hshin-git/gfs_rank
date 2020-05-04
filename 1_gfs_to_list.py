###########################################
## GFSファイルから気象変数リストを作成
###########################################
#import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
import sys,datetime

###########################################
## コマンドライン引数: GFSファイル指定
GFS_PATH = "./gfs/gfs_2020042012_168.nc"
GFS_PATH = sys.argv[1] if len(sys.argv)>1 else GFS_PATH
OUT_PATH = "./info"
##
print("argv:",sys.argv)
print("gfs:",GFS_PATH)
print("out:",OUT_PATH)

###########################################
## GFSファイルの参照開始
ds = xr.open_dataset(GFS_PATH)

###########################################
COLS = [
# 追加属性
 'LAYERS',
 'DIMENSION',
 'dims',
# GRIB属性
 'long_name',
 'units',
 'abbreviation',
 'grid_mapping',
 'Grib_Variable_Id',
 'Grib2_Parameter',
 'Grib2_Parameter_Discipline',
 'Grib2_Parameter_Category',
 'Grib2_Parameter_Name',
 'Grib2_Level_Type',
 'Grib2_Level_Desc',
 'Grib2_Generating_Process_Type'
]

## データフレームの準備
INFO = pd.DataFrame(index=sorted(ds.variables),columns=COLS)
INFO.index.name = "GFS"

for k in sorted(ds.variables)[:]:
  v = ds[k]
  a = v.attrs
  d = v.dims	#time,(isobalic,)lat,lon
  n = len(v.dims)
  print(k,len(a),len(d))
  # 追加属性
  if n<3:	#time,lat,lon
    INFO.loc[k,COLS[0]] = 0
  elif n==3:	#sea/land surface
    INFO.loc[k,COLS[0]] = 1
  elif n==4:	#isobaric surface
    INFO.loc[k,COLS[0]] = len(v[d[1]])
  INFO.loc[k,COLS[1]] = n
  INFO.loc[k,COLS[2]] = d
  # GRIB属性
  for c in a:
    if c in COLS: INFO.loc[k,c] = a[c]

###########################################
## GFSファイルの参照終了
ds.close()

## CSV保存
INFO = INFO[INFO.LAYERS>0]
INFO.to_csv(OUT_PATH + "/" + "gfs_list.csv",index=True)

###########################################

