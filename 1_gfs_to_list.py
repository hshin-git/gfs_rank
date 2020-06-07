##################################################
## GFSファイルから気象変数リストを作成
##################################################
#import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
import os,sys
from datetime import datetime
import COMMON as COM


##################################################
## コマンドライン引数: GFSファイル指定
GFS_PATH = "./gfs/gfs_2020042012_168.nc"
GFS_PATH = sys.argv[1] if len(sys.argv)>1 else GFS_PATH
OUT_PATH = COM.INFO_PATH	#"./info"
##
print("enter:", sys.argv)
print(sys.argv[0], datetime.now())
print(sys.argv[0], GFS_PATH)
print(sys.argv[0], OUT_PATH)
os.makedirs(OUT_PATH, exist_ok=True)


##################################################
## GFSファイルの参照開始
ds = xr.open_dataset(GFS_PATH)

##################################################
COLS = [
# 追加属性
 'LAYERS',
 'DIMENSION',
 'Coordinates',
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
 'Grib2_Generating_Process_Type',
# 座標属性
 'positive',
 'Grib_level_type',
 '_CoordinateAxisType',
 '_CoordinateZisPositive',
 'length',
 'values',
]

## データフレームの準備
INFO = pd.DataFrame(index=sorted(ds.variables),columns=COLS)
INFO.index.name = "GFS"

for k in sorted(ds.variables)[:]:
  v = ds[k]
  a = v.attrs
  d = v.dims	#time,(isobalic,)lat,lon
  n = len(v.dims)
  print(sys.argv[0], k,len(a),len(d))
  # 追加属性
  if n<3:	#coordinate axis
    INFO.loc[k,COLS[0]] = 0
    INFO.loc[k,COLS[-2]] = v.values.size
    INFO.loc[k,COLS[-1]] = ";".join(["%s"%e for e in (v.values[:min(10,v.values.size)] if n>0 else [v.values])])
  elif n==3:	#sea/land surface
    INFO.loc[k,COLS[0]] = 1
  elif n==4:	#isobaric surface
    INFO.loc[k,COLS[0]] = len(v[d[1]])
  INFO.loc[k,COLS[1]] = n
  INFO.loc[k,COLS[2]] = d
  # GRIB属性
  for c in a:
    if c in COLS: INFO.loc[k,c] = a[c]

##################################################
## GFSファイルの参照終了
ds.close()

## CSV保存
LIST = INFO[INFO.LAYERS>0][COLS[:-6]]
AXIS = INFO[INFO.LAYERS==0][COLS[:5]+COLS[15:]]
LIST.to_csv(OUT_PATH +"/"+ "gfs_list.csv",index=True)
AXIS.to_csv(OUT_PATH +"/"+ "gfs_axis.csv",index=True)

##################################################
print("leave:", sys.argv)
sys.exit(0)

