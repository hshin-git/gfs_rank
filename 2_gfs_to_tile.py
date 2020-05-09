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
GFS_PATH = "./gfs/gfs_2020042012_168.nc"
GFS_PATH = sys.argv[1] if len(sys.argv) > 1 else GFS_PATH

VAR_LIST = ["Visibility_surface"]
VAR_LIST = sys.argv[2:] if len(sys.argv) > 2 else VAR_LIST

## ファイル出力場所
OUT_PATH = COM.TILE_PATH	#"./tile"
print("argv:",sys.argv)
print("date:",datetime.now())
print("gfs:",GFS_PATH)
print("out:",OUT_PATH)
os.makedirs(OUT_PATH, exist_ok=True)


###########################################
## 可視化オプション
VIS_OPTS = {
## VariableName:['cmap':ColorMap,'clip':[PercentileMin,PercentileMax],'vclip':[ValueMin,ValueMax],'conv':[ConvFun, NewUnit]]
	'Temperature_surface':{'cmap':'coolwarm','clip':[5,95],'conv':[lambda x: x-273.15,'degC']},
	'Wind_speed_gust_surface':{'cmap':'Greens','clip':[70,100]},
	'Categorical_Rain_surface':{'cmap':'Blues','vclip':[0.5,1.2]},
	'Categorical_Snow_surface':{'cmap':'Greys','vclip':[0.5,1.0]},
	'Categorical_Ice_Pellets_surface':{'cmap':'Purples'},
	'Downward_Short-Wave_Radiation_Flux_surface_Mixed_intervals_Average':{'cmap':'Reds','vclip':[100,1100]},
	'Sunshine_Duration_surface':{'cmap':'Reds', 'vclip':[0.1,1.0], 'conv':[lambda x: x/(3600*6.),'%']},
	'Visibility_surface':{'cmap':'Greys_r', 'clip':[0,20], 'conv':[lambda x: x/1000.,'km']},
	'Temperature_isobaric':{'cmap':'coolwarm','conv':[lambda x: x-273.15,'degC']},
	'Relative_humidity_isobaric':{},
	'Geopotential_height_isobaric':{'cmap':'terrain','conv':[lambda x: x/9.8,'m']},
	'Total_cloud_cover_isobaric':{'cmap':'Purples'},
# test
	'5-Wave_Geopotential_Height_isobaric':{},
}
# default
for v in VAR_LIST:
  if not(v in VIS_OPTS): VIS_OPTS[v] = {}


## プロットのパラメータ
WEST,EAST,SOUTH,NORTH = 115,155,20,50
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
for NAME in VAR_LIST:
  # データ準備
  data_var = data.variables[NAME]
  UNIT = data_var.units
  ABBR = data_var.abbreviation
  data_vals = data_var[:].squeeze()
  DIMS = len(data_vals.shape)

  # 時間座標
  reftime_var = data.variables["reftime"]
  reftime_vals = num2date(reftime_var[:].squeeze(), reftime_var.units)

  time_var = data.variables["time"]
  time_vals = num2date(time_var[:].squeeze(), time_var.units)

  # 水平座標
  lat_vals = data.variables["lat"][:].squeeze()
  lon_vals = data.variables["lon"][:].squeeze()

  lon_2d, lat_2d = np.meshgrid(lon_vals, lat_vals)

  # 気圧座標
  ATTR = data_var.coordinates.split()	# reftime time (alt) lat lon
  if DIMS==3:	# time,lat,lon
    alt_vals = [0]
  elif DIMS==4:	# time,alt,lat,lon
    alt_var = data.variables[ATTR[-3]]
    alt_unit = alt_var.units
    alt_vals = alt_var[:].squeeze()
  else:
    print("skip:", NAME)
    continue

  ###########################################
  NT = len(time_vals[:])
  NZ = len(alt_vals)
  for t in range(0,NT,TIME_STEP):
    # 時刻ラベル設定
    UTC = time_vals[t]
    JST = UTC + timedelta(hours=TIME_ZONE)
    REFT = reftime_vals[t]
    INIT = REFT.strftime("%Y%m%d%H")
    FT = int((UTC-REFT).days*24 + (UTC-REFT).seconds/3600)

    for z in range(0,NZ,HGHT_STEP):
      DATA = data_vals[t] if DIMS==3 else data_vals[t,z]
      DATA_ = data_vals[:,:,:] if DIMS==3 else data_vals[:,z,:,:]

      # 画像ファイル名
      #PNG_PATH = OUT_PATH + "/" + "%s_%02d_%s_%03d.png"%(NAME,z,INIT,t*3)
      PNG_PATH = OUT_PATH + "/" + "%s_%02d_%03d.png"%(NAME,z,t*3)
      print("plot:", JST, ABBR, z, NAME)

      # 表示オプション
      OPTS = VIS_OPTS[NAME]
      CMAP = "Blues"
      PMIN,PMAX = 1,99
      CONV = np.vectorize(lambda x: x)

      if 'cmap' in OPTS:
        CMAP = OPTS['cmap']
      if 'conv' in OPTS:
        CONV = np.vectorize(OPTS['conv'][0])
        UNIT = OPTS['conv'][1]
        DATA = CONV(DATA)
      if 'clip' in OPTS:
        PMIN,PMAX = OPTS['clip']

      VMIN = CONV(np.percentile(DATA_,PMIN))
      VMAX = CONV(np.percentile(DATA_,PMAX))
      if 'vclip' in OPTS:
        VMIN,VMAX = OPTS['vclip']
      LEVS = np.linspace(VMIN,VMAX,20)

      DATA = np.ma.masked_array(DATA)
      DATA.mask = (DATA<VMIN) | (DATA>VMAX)

      ###########################################
      TITLE = 'JST%s (UTC%s + %03dh)'%(JST.strftime("%Y-%m-%d %H:%M"), REFT.strftime("%Y%m%d_%H%M"), FT)
      VNAME = "%s_%02d%s (%s)"%(NAME,alt_vals[z],"" if DIMS==3 else alt_unit,UNIT)
      PROJ = ccrs.PlateCarree()
      #PROJ = ccrs.Stereographic(central_latitude=(SOUTH+NORTH)/2,central_longitude=(WEST+EAST)/2)

      # プロット作成
      fig = plt.figure(figsize=PLOT_SIZE)

      # Add the map and set the extent
      ax = fig.add_subplot(1,1,1,projection=PROJ)
      ax.set_extent([WEST,EAST,SOUTH,NORTH], PROJ)
      ax.set_xmargin(0)
      ax.set_ymargin(0)

      # Contour temperature at each lat/long
      #cf = ax.contourf(lon_2d, lat_2d, DATA, LEVS, alpha=PLOT_ALPHA, cmap=CMAP)
      cf = ax.pcolormesh(lon_2d,lat_2d,DATA,transform=PROJ,vmin=VMIN,vmax=VMAX,alpha=PLOT_ALPHA,cmap=CMAP)#, snap=True,shading='flat')

      # make tile for WMS
      if PLOT_TILE:
        ax.coastlines('50m', linewidth=1, color=COAST_COLOR, alpha=PLOT_ALPHA)
        ax.text(WEST+5,SOUTH+1,VNAME + "\n" + TITLE, bbox=dict(boxstyle="round",facecolor='white'))
        ax.outline_patch.set_visible(False)
        ax.background_patch.set_visible(False)
        # Save plot
        plt.savefig(PNG_PATH, transparent=True, bbox_inches='tight')
      else:
        # Add state boundaries to plot
        ax.coastlines('50m', linewidth=1, color=COAST_COLOR, alpha=PLOT_ALPHA)
        gl = ax.gridlines(crs=PROJ, draw_labels=True, linewidth=1, color=COAST_COLOR, alpha=PLOT_ALPHA, linestyle='--')
        gl.xlocator = mticker.FixedLocator(np.arange(0,360,5))
        gl.ylocator = mticker.FixedLocator(np.arange(-90,90,5))
        # Add colorbar and title to plot
        ax.set_title(TITLE+"\n")
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

