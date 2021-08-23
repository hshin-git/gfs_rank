import matplotlib as mpl
mpl.use('Agg')
###########################################
## NCSS to Plot
###########################################
import numpy as np
import pandas as pd
import xarray as xr

import os,sys,shutil
from datetime import datetime,timedelta

import matplotlib.pyplot as plt

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.ticker as mticker
from cartopy.mpl.ticker import LatitudeFormatter,LongitudeFormatter

import netCDF4
from netCDF4 import num2date

import COMMON as COM



###########################################
## コマンドライン引数: GFSファイル名、変数名リスト
GFS_PATH = "./gfs/gfs_2021081412_168.nc"
GFS_PATH = sys.argv[1] if len(sys.argv) > 1 else GFS_PATH


## ファイル出力場所
OUT_PATH = COM.TILE_PATH	#"./tile"
print("argv:",sys.argv)
print("date:",datetime.now())
print("gfs:",GFS_PATH)
print("out:",OUT_PATH)
os.makedirs(OUT_PATH, exist_ok=True)


###########################################
## 可視化オプション
## プロットのパラメータ
WEST,EAST,SOUTH,NORTH = COM.AREA
PLOT_TILE = False
PLOT_ALPHA = 0.5
PLOT_SIZE = (12,12)

COAST_COLOR = 'black'#'red'#'gray'

TIME_ZONE = 9
TIME_STEP = 1
HGHT_STEP = 10

## パラメータの表示
print("time_step",TIME_STEP)
print("hght_step",HGHT_STEP)


###########################################
# GFSデータの参照開始
data =  netCDF4.Dataset(GFS_PATH, 'r')

  
# We'll pull out the useful variables for temperature, latitude, and longitude, and time
# (which is the time, in hours since the forecast run).
for NAME in sorted(data.variables)[:]:
  # データ準備
  data_var = data.variables[NAME]
  data_vals = data_var[:].squeeze()
  DIMS = len(data_vals.shape)

  # 3D/4D変数のみ
  if DIMS == 3:
    DATA = data_vals
  elif DIMS == 4:
    DATA = data_vals[:,0,:,:]
  else:
    print("skip:", NAME)
    continue

  UNIT = data_var.units
  ABBR = data_var.abbreviation
  LONG = data_var.long_name

  # 最小と最大
  DMIN = np.amin(DATA,axis=0)
  DMAX = np.amax(DATA,axis=0)
  
  # 時間座標
  reftime_var = data.variables["reftime"]
  reftime_vals = num2date(reftime_var[:].squeeze(), reftime_var.units)

  time_var = data.variables["time"]
  time_vals = num2date(time_var[:].squeeze(), time_var.units)

  # 水平座標
  lat_vals = data.variables["lat"][:].squeeze()
  lon_vals = data.variables["lon"][:].squeeze()

  lon_2d, lat_2d = np.meshgrid(lon_vals, lat_vals)
  
  
  #sys.exit(0)
  ###########################################
  # 時刻ラベル設定
  UTC = time_vals[0]
  UTC1 = time_vals[-1]
  JST = UTC + timedelta(hours=TIME_ZONE)
  REFT = reftime_vals[0]
  INIT = REFT.strftime("%Y%m%d%H")
  FT = int((UTC1-REFT).days*24 + (UTC1-REFT).seconds/3600)
  
  # 画像ファイル名
  PNG_PATH = OUT_PATH + "/" + "%s.png"%(NAME)
  print("plot:", JST, ABBR, NAME)

  # 表示オプション
  CMAP = "Blues"
  

  ###########################################
  TITLE = '%s\nfrom JST%s (UTC%s) to +%03dh'%(LONG,JST.strftime("%Y-%m-%d %H:%M"), REFT.strftime("%Y%m%d_%H%M"), FT)
  PROJ = ccrs.PlateCarree()
  #PROJ = ccrs.Stereographic(central_latitude=(SOUTH+NORTH)/2,central_longitude=(WEST+EAST)/2)

  # プロット作成
  fig = plt.figure(figsize=PLOT_SIZE)

  ##### PLOT MAX #####
  VNAME = "MAX of %s (%s)"%(ABBR,UNIT)
  # Add the map and set the extent
  ax = fig.add_subplot(2,1,1,projection=PROJ)
  ax.set_extent([WEST,EAST,SOUTH,NORTH], PROJ)
  ax.set_xmargin(0)
  ax.set_ymargin(0)

  # Contour temperature at each lat/long
  #cf = ax.contourf(lon_2d, lat_2d, DATA, LEVS, alpha=PLOT_ALPHA, cmap=CMAP)
  cf = ax.pcolormesh(lon_2d,lat_2d,DMAX,transform=PROJ,vmin=np.min(DMAX),vmax=np.max(DMAX),alpha=PLOT_ALPHA,cmap=CMAP)#, snap=True,shading='flat')

  # make tile for WMS
  # Add state boundaries to plot
  ax.coastlines('50m', linewidth=1, color=COAST_COLOR, alpha=PLOT_ALPHA)
  gl = ax.gridlines(crs=PROJ, draw_labels=True, linewidth=1, color=COAST_COLOR, alpha=PLOT_ALPHA, linestyle='--')
  gl.xlocator = mticker.FixedLocator(np.arange(0,360,5))
  gl.ylocator = mticker.FixedLocator(np.arange(-90,90,5))
  # Add colorbar and title to plot
  ax.set_title(TITLE+"\n")
  cb = plt.colorbar(cf, ax=ax, fraction=0.02)
  cb.set_label(VNAME)

  ##### PLOT MIN #####
  VNAME = "MIN of %s (%s)"%(ABBR,UNIT)
  # Add the map and set the extent
  ax = fig.add_subplot(2,1,2,projection=PROJ)
  ax.set_extent([WEST,EAST,SOUTH,NORTH], PROJ)
  ax.set_xmargin(0)
  ax.set_ymargin(0)

  # Contour temperature at each lat/long
  #cf = ax.contourf(lon_2d, lat_2d, DATA, LEVS, alpha=PLOT_ALPHA, cmap=CMAP)
  cf = ax.pcolormesh(lon_2d,lat_2d,DMIN,transform=PROJ,vmin=np.min(DMIN),vmax=np.max(DMIN),alpha=PLOT_ALPHA,cmap=CMAP)#, snap=True,shading='flat')

  # make tile for WMS
  # Add state boundaries to plot
  ax.coastlines('50m', linewidth=1, color=COAST_COLOR, alpha=PLOT_ALPHA)
  gl = ax.gridlines(crs=PROJ, draw_labels=True, linewidth=1, color=COAST_COLOR, alpha=PLOT_ALPHA, linestyle='--')
  gl.xlocator = mticker.FixedLocator(np.arange(0,360,5))
  gl.ylocator = mticker.FixedLocator(np.arange(-90,90,5))
  # Add colorbar and title to plot
  #ax.set_title(TITLE+"\n")
  cb = plt.colorbar(cf, ax=ax, fraction=0.02)
  cb.set_label(VNAME)


  # Save plot
  plt.savefig(PNG_PATH, bbox_inches='tight')

  # close figure
  plt.close()

###########################################
## GFSデータの参照終了
data.close()

##################################################
sys.exit(0)

