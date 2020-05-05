"""
700-hPa Relative Humidity
=========================

Classic 700-hPa Map that displays Relative Humidity

By: Kevin Goebbert

This example uses GFS output to displays common 700-hPa parameters
including relative humidity.

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
# Import needed modules
#

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import metpy.calc as mpcalc
from metpy.units import units
import numpy as np
import xarray as xr
plt.style.use(COM.MPLSTYLE)


######################################################################
# Access data using Xarray
#
"""
ds = xr.open_dataset('https://thredds.ucar.edu/thredds/dodsC/casestudies/'
                     'python-gallery/GFS_20101026_1200.nc').metpy.parse_cf()
"""
ds = xr.open_dataset(GFS_PATH).metpy.parse_cf()

# Fix units on Relative Humidity
ds.Relative_humidity_isobaric.attrs['units'] = 'percent'

######################################################################
# Data Parsing
# ------------
#
# Parse out desired data and attach units.
#
# Smooth using MetPy’s ``smooth_gaussian`` function to minimize noise in
# output.
#

# Set subset slice for the geographic extent of data to limit download
"""
lon_slice = slice(200, 350)
lat_slice = slice(85, 10)
"""
lon_slice = slice(WEST, EAST)
lat_slice = slice(NORTH, SOUTH)

# Grab lat/lon values (GFS will be 1D)
lats = ds.lat.sel(lat=lat_slice).values
lons = ds.lon.sel(lon=lon_slice).values

# Select specific level data
level = 700 * units.hPa
hght_700 = mpcalc.smooth_gaussian(ds['Geopotential_height_isobaric'].metpy.sel(
    vertical=level, lon=lon_slice, lat=lat_slice).squeeze(), 2)
tmpk_700 = mpcalc.smooth_gaussian(ds['Temperature_isobaric'].metpy.sel(
    vertical=level, lon=lon_slice, lat=lat_slice).squeeze(), 2)
uwnd_700 = mpcalc.smooth_gaussian(ds['u-component_of_wind_isobaric'].metpy.sel(
    vertical=level, lon=lon_slice, lat=lat_slice).squeeze(), 2)
vwnd_700 = mpcalc.smooth_gaussian(ds['v-component_of_wind_isobaric'].metpy.sel(
    vertical=level, lon=lon_slice, lat=lat_slice).squeeze(), 2)
relh_700 = mpcalc.smooth_gaussian(ds['Relative_humidity_isobaric'].metpy.sel(
    vertical=level, lon=lon_slice, lat=lat_slice).squeeze(), 2)

# Convert temperature to Celsius for plotting purposes
tmpc_700 = tmpk_700.to('degC')

# Get times in nice datetime format
"""
vtime = ds.time.data.squeeze().astype('datetime64[ms]').astype('O')
"""
vtime = ds.time.data[t].astype('datetime64[ms]').astype('O')
# 時間スライスの追加
hght_700 = hght_700[t]
tmpk_700 = tmpk_700[t]
uwnd_700 = uwnd_700[t]
vwnd_700 = vwnd_700[t]
relh_700 = relh_700[t]
tmpc_700 = tmpc_700[t]

# 平滑化
from scipy.ndimage import gaussian_filter
SIGMA = 3.0/1.5
hght_700 = gaussian_filter(hght_700,sigma=SIGMA)
tmpc_700 = gaussian_filter(tmpc_700,sigma=SIGMA)
#sys.exit(0)


######################################################################
# Plot Data
# ---------
#
# Use Cartopy to plot 700-hPa data on a Lambert Conformal Map and
# colorfill the relative humidity
#

# Set graphic projection
"""
mapcrs = ccrs.LambertConformal(central_longitude=-100, central_latitude=35,
                               standard_parallels=(30, 60))
"""
mapcrs = ccrs.LambertConformal(central_longitude=(WEST+EAST)/2, central_latitude=(SOUTH+NORTH)/2,
                               standard_parallels=(30, 60))


# Set data projection
datacrs = ccrs.PlateCarree()

# Begin figure and set CONUS areal extent
fig = plt.figure(1, figsize=COM.FIGSIZE)
ax = plt.subplot(111, projection=mapcrs)
"""
ax.set_extent([-130, -72, 20, 55], ccrs.PlateCarree())
"""
ax.set_extent([WEST, EAST, SOUTH, NORTH], ccrs.PlateCarree())
ax.set_xmargin(0)
ax.set_ymargin(0)

# Add coastlines and state boundaries
ax.add_feature(cfeature.COASTLINE.with_scale('50m'))
ax.add_feature(cfeature.STATES.with_scale('50m'))

# Plot Colorfill of 700-hPa relative humidity -
# normalize color to not have too dark of green at the top end
clevs_700_relh = np.arange(80, 100+1, 5)
cf = ax.contourf(lons, lats, relh_700, clevs_700_relh, cmap=plt.cm.Purples,
                 norm=plt.Normalize(80, 120), transform=datacrs)
cb = plt.colorbar(cf, orientation='horizontal', pad=0, aspect=50, shrink=COM.SHRINK)
cb.set_label('Rel. Humidity (%)')

# Plot contours of 700-hPa temperature in Celsius in red, dashed lines
clevs_700_tmpc = np.arange(-42, 42+1, 3)
cs1 = ax.contour(lons, lats, tmpc_700, clevs_700_tmpc, colors='tab:red',linewidths=COM.LINEWIDTH,
	linestyles='dashed', transform=datacrs)
ax.clabel(cs1, fmt='%d', fontsize=COM.FONTSIZE)

# Plot contours of 700-hPa geopotential height in black, solid lines
clevs_700_hght = np.arange(0, 8000, 30)
cs2 = ax.contour(lons, lats, hght_700, clevs_700_hght, colors='black', linewidths=COM.LINEWIDTH,
	transform=datacrs)
ax.clabel(cs2, fmt='%d', fontsize=COM.FONTSIZE)

# Plot 700-hPa wind barbs in knots
ax.barbs(lons, lats, uwnd_700.to('kt').m, vwnd_700.to('kt').m, pivot='middle',
         color='grey', regrid_shape=20, transform=datacrs)

# Add some useful titles
"""
plt.title('GFS 700-hPa Geopotential Heights (m), Temperature (C),'
          ' and Wind Barbs (kt)', loc='left')
plt.title('Valid Time: JST {}'.format(vtime+timedelta(hours=9)), loc='right')
plt.show()
"""
plt.title('GFS 700-hPa Heights (m), Temp. (C), and Wind Barbs (kt)', loc='left',fontsize=COM.FONTSIZE)
plt.title('JST {}'.format(vtime+timedelta(hours=9)), loc='right',fontsize=COM.FONTSIZE)

plt.savefig(OUT_PATH, transparent=COM.TRANSPARENT) #bbox_inches='tight',pad_inches=COM.PAD_INCHES)
# Close all
plt.close(fig)
ds.close()

