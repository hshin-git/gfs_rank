"""
500 hPa Geopotential Heights and Winds
======================================

Classic 500-hPa plot using NAM analysis file.

This example uses example data from the NAM anlysis for 12 UTC 31
October 2016 and uses xarray as the main read source with using Cartopy
for plotting a CONUS view of the 500-hPa geopotential heights, wind
speed, and wind barbs.

"""
######################################################################
import matplotlib as mpl
mpl.use('Agg')
import os,sys
from datetime import timedelta
import COMMON as COM

## コマンドライン引数: 時間コマ
GFS_PATH = "./gfs/gfs_2020042312_168.nc"
GFS_PATH = sys.argv[1] if len(sys.argv) > 1 else GFS_PATH
t = 0
t = int(sys.argv[2]) if len(sys.argv) > 2 else t

## GFSデータの空間範囲: 経度と緯度
WEST,EAST,SOUTH,NORTH = COM.AREA	#115,155,20+5,50

## 出力ファイル名
os.makedirs(COM.CHRT_PATH, exist_ok=True)
SCR_NAME = os.path.basename(sys.argv[0]).split('.')[0]
OUT_PATH = "%s/%s_%03d.png"%(COM.CHRT_PATH,SCR_NAME[9:],t*3)
print("argv:",sys.argv)
print("gfs:",GFS_PATH)
print("out:",OUT_PATH)


######################################################################
# Import the needed modules.
#

from datetime import datetime

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import metpy.calc as mpcalc
from metpy.units import units
import numpy as np
from scipy.ndimage import gaussian_filter
import xarray as xr
plt.style.use(COM.MPLSTYLE)

######################################################################
# The following code reads the example data using the xarray open_dataset
# function and prints the coordinate values that are associated with the
# various variables contained within the file.
#
"""
ds = xr.open_dataset('https://thredds.ucar.edu/thredds/dodsC/casestudies/'
                     'python-gallery/NAM_20161031_1200.nc')
ds.coords
"""
ds = xr.open_dataset(GFS_PATH).metpy.parse_cf()


######################################################################
# Data Retrieval
# --------------
#
# This code retrieves the necessary data from the file and completes some
# smoothing of the geopotential height and wind fields using the SciPy
# function gaussian_filter. A nicely formated valid time (vtime) variable
# is also created.
#

# Grab lat/lon values (NAM will be 2D)
lats = ds.lat.data
lons = ds.lon.data

# Select and grab data
tmpk = ds['Temperature_isobaric']
hght = ds['Geopotential_height_isobaric']
uwnd = ds['u-component_of_wind_isobaric']
vwnd = ds['v-component_of_wind_isobaric']

# Select and grab 500-hPa geopotential heights and wind components, smooth with gaussian_filter
tmpk_500 = gaussian_filter(tmpk.sel(isobaric6=300*100).data[t], sigma=3.0)
hght_500 = gaussian_filter(hght.sel(isobaric6=300*100).data[t], sigma=3.0)
#uwnd_500 = gaussian_filter(uwnd.sel(isobaric=300*100).data[t], sigma=3.0) * units('m/s')
#vwnd_500 = gaussian_filter(vwnd.sel(isobaric=300*100).data[t], sigma=3.0) * units('m/s')
uwnd_500 = uwnd.sel(isobaric=300*100).data[t] * units('m/s')
vwnd_500 = vwnd.sel(isobaric=300*100).data[t] * units('m/s')

# Use MetPy to calculate the wind speed for colorfill plot, change units to knots from m/s
sped_500 = mpcalc.wind_speed(uwnd_500, vwnd_500).to('kt')

# Create a clean datetime object for plotting based on time of Geopotential heights
"""
vtime = datetime.strptime(str(ds.time.data[0].astype('datetime64[ms]')),
                          '%Y-%m-%dT%H:%M:%S.%f')
"""
vtime = datetime.strptime(str(ds.time.data[t].astype('datetime64[ms]')),
                          '%Y-%m-%dT%H:%M:%S.%f')
# 時間スライスの追加
"""
hght_500 = hght_500[t]
uwnd_500 = uwnd_500[t]
vwnd_500 = vwnd_500[t]
"""
#sys.exit(0)


######################################################################
# Map Creation
# ------------
#
# This next set of code creates the plot and draws contours on a Lambert
# Conformal map centered on -100 E longitude. The main view is over the
# CONUS with geopotential heights contoured every 60 m and wind speed in
# knots every 20 knots starting at 30 kt.
#

# Set up the projection that will be used for plotting
"""
mapcrs = ccrs.LambertConformal(central_longitude=-100,
                               central_latitude=35,
                               standard_parallels=(30, 60))
"""
mapcrs = ccrs.LambertConformal(central_longitude=(WEST+EAST)/2, central_latitude=(SOUTH+NORTH)/2,
                               standard_parallels=(30, 60))

# Set up the projection of the data; if lat/lon then PlateCarree is what you want
datacrs = ccrs.PlateCarree()

# Start the figure and create plot axes with proper projection
fig = plt.figure(1, figsize=COM.FIGSIZE)
ax = plt.subplot(111, projection=mapcrs)
"""
ax.set_extent([-130, -72, 20, 55], ccrs.PlateCarree())
"""
ax.set_extent([WEST, EAST, SOUTH, NORTH], ccrs.PlateCarree())
ax.set_xmargin(0)
ax.set_ymargin(0)

# Add geopolitical boundaries for map reference
ax.add_feature(cfeature.COASTLINE.with_scale('50m'))
ax.add_feature(cfeature.STATES.with_scale('50m'))

# Plot 500-hPa Colorfill Wind Speeds in knots
clevs_500_sped = np.arange(60, 160+1, 20)
cf = ax.contourf(lons, lats, sped_500, clevs_500_sped, cmap=plt.cm.GnBu,
                 transform=datacrs)
cb = plt.colorbar(cf, orientation='horizontal', pad=0, aspect=50, shrink=COM.SHRINK)
cb.set_label('Wind Speed (kt)')

# Plot 500-hPa Geopotential Heights in meters
clevs_500_hght = np.arange(0, 12000, 60*2)
cs = ax.contour(lons, lats, hght_500, clevs_500_hght, colors='black', linewidths=COM.LINEWIDTH,
                transform=datacrs)
plt.clabel(cs, fmt='%d',fontsize=COM.FONTSIZE)

# Plot 500-hPa Temperature in degC
clevs_500_temp = np.arange(-60, 60, 3)
cs = ax.contour(lons, lats, tmpk_500-273.15, clevs_500_temp, colors='tab:red', linewidths=COM.LINEWIDTH,
                transform=datacrs)
plt.clabel(cs, fmt='%d', fontsize=COM.FONTSIZE)

# Plot 500-hPa wind barbs in knots, regrid to reduce number of barbs
ax.barbs(lons, lats, uwnd_500.to('kt').m, vwnd_500.to('kt').m, pivot='middle',
         color='grey', regrid_shape=20, transform=datacrs)

# Make some nice titles for the plot (one right, one left)
"""
plt.title('GFS 300-hPa Geopotential Heights (m), Wind Speed (kt),'
          ' and Temperature (C)', loc='left')
plt.title('Valid Time: JST {}'.format(vtime+timedelta(hours=9)), loc='right')
"""
plt.title('GFS 300-hPa Heights (m), Wind Speed (kt), and Temp. (C)', loc='left',fontsize=COM.FONTSIZE)
plt.title('JST {}'.format(vtime+timedelta(hours=9)), loc='right',fontsize=COM.FONTSIZE)

# Adjust image and show
#plt.subplots_adjust(bottom=0, top=1)

#plt.show()
plt.savefig(OUT_PATH, transparent=COM.TRANSPARENT) #bbox_inches='tight',pad_inches=COM.PAD_INCHES)
# Close all
plt.close(fig)
ds.close()

