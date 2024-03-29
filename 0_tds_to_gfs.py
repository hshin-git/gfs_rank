###########################################
## 日本周辺のGFSデータを取得してファイル保存
###########################################
import numpy as np
import pandas as pd
import os,sys,shutil
#import matplotlib.pyplot as plt
from datetime import datetime,timedelta

from netCDF4 import num2date
from siphon.catalog import TDSCatalog
import xarray as xr

import COMMON as COM

###########################################
print("argv:",sys.argv)
print("date:",datetime.now())
## コマンドライン引数: 開始年月日(YYYYMMDD)、予報期間(日)
NOW = datetime.utcnow()
NOW = datetime.strptime(sys.argv[1][:8],"%Y%m%d") if len(sys.argv) > 1 else NOW

DAYS = 7
DAYS = int(sys.argv[2]) if len(sys.argv) > 2 else DAYS

###########################################
## GFSデータの初期時刻: 開始時の整列
INZ = (0,6,12,18)[2]

## GFSデータの時間範囲: UTC1からUTC2
if len(sys.argv) > 1:
  UTC1 = datetime(NOW.year,NOW.month,NOW.day,INZ)
else:
  DD = 0 if NOW.hour >= INZ else 1
  UTC1 = datetime(NOW.year,NOW.month,NOW.day,INZ) - timedelta(days=DD)

UTC2 = UTC1 + timedelta(days=DAYS)
print("utc1:", UTC1)
print("utc2:", UTC2)
#sys.exit(0)

###########################################
## GFSデータの空間範囲: 経度と緯度
WEST,EAST,SOUTH,NORTH = 115,155,20,50
print("area:", WEST,EAST,SOUTH,NORTH)

## GFSデータの保存先
OUT_PATH = COM.DATA_PATH	#"./gfs"
GFS_YMDH = UTC1.strftime("%Y%m%d%H")
GFS_FCST = DAYS * 24
GFS_PATH = OUT_PATH + "/" + "gfs_%s_%03d.nc"%(GFS_YMDH,GFS_FCST)
if os.path.exists(GFS_PATH):
  print("error:", GFS_PATH, "already exists.")
  sys.exit(0)
os.makedirs(OUT_PATH, exist_ok=True)

###########################################
## GFSデータの取得先
TDS_LIST = [
	'http://thredds.ucar.edu/thredds/catalog/grib/NCEP/GFS/',
	'https://thredds-jumbo.unidata.ucar.edu/thredds/catalog/grib/NCEP/GFS/',
	'http://thredds-jetstream.unidata.ucar.edu/thredds/catalog/grib/NCEP/GFS/',
]
TDS_PATH = [
	'Global_0p25deg/catalog.xml?dataset=grib/NCEP/GFS/Global_0p25deg/Best',
	'Global_0p25deg_ana/catalog.xml?dataset=grib/NCEP/GFS/Global_0p25deg_ana/TP',
	'Global_0p5deg/catalog.xml?dataset=grib/NCEP/GFS/Global_0p5deg/Best',
][2]

###########################################
for TDS_ROOT in TDS_LIST:
  print("server:", TDS_ROOT)
  print("catalog:", TDS_PATH)
  ###########################################
  try:
    best_gfs = TDSCatalog(TDS_ROOT + TDS_PATH)
    print("datasets:", list(best_gfs.datasets))
    ###########################################
    best_ds = best_gfs.datasets[0]
    ncss = best_ds.subset()
    ###########################################
    query = ncss.query()
    query.lonlat_box(north=NORTH, south=SOUTH, east=EAST, west=WEST).time_range(UTC1,UTC2)
    query.accept('netcdf4')
    query.variables('all')
    print("query:","...")
    data = ncss.get_data(query)
  except:
    print("query:","error")
    if TDS_ROOT != TDS_LIST[-1]:
      print("query:","retry")
      continue
    else:
      print("query:","abort")
      sys.exit(-1)
  else:
    print("query:","done")
    break

###########################################
## convert netcdf to xarray
ds = xr.open_dataset(xr.backends.NetCDF4DataStore(data))

# check gfs
REFT = pd.to_datetime(ds['reftime'].values)
TIME = pd.to_datetime(ds['time'].values)
DT = TIME[-1] - REFT[0]
FT = int(DT.days*24 + DT.seconds/3600)
YMDH = REFT[0].strftime("%Y%m%d%H")
if (YMDH!=GFS_YMDH) or (FT!=GFS_FCST):
  print("error:", GFS_PATH, "may has missing data.")

# save gfs
print("gfs_path:",GFS_PATH)
ds.to_netcdf(GFS_PATH)
ds.close()

###########################################
#data.close()
sys.exit(0)
