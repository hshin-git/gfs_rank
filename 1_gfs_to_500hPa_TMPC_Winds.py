"""
850-hPa Geopotential Heights, Temperature, and Winds
====================================================

Classic 850-hPa with Geopotential Heights, Temperature, and Winds

This example uses example data from the GFS analysis for 12 UTC 26
October 2010 and uses xarray as the main read source with using MetPy to
calculate frontogenesis and wind speed with geographic plotting using
Cartopy for a CONUS view.

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
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from metpy.units import units
import numpy as np
import xarray as xr
import scipy.ndimage as ndimage
plt.style.use(COM.MPLSTYLE)


######################################################################
# Use Xarray to read netCDF data from a remote server and use MetPy’s
# parse_cf() capability to make it easy to get arrays with attached units.
#
"""
ds = xr.open_dataset('https://thredds.ucar.edu/thredds/dodsC/casestudies/'
                     'python-gallery/GFS_20101026_1200.nc').metpy.parse_cf()
"""
ds = xr.open_dataset(GFS_PATH).metpy.parse_cf()


######################################################################
# Subset Data
# -----------
#
# Bring in individual variables and subset for domain that is being
# analyzed (roughly CONUS). There are a couple of MetPy helpers being used
# here to get arrays with units (``.metpy.unit_array``) and selecting on a
# generic “vertical” domain.
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

# Set level to plot/analyze
level = 500 * units.hPa

# Grad individual data arrays with units from our file, selecting for level and lat/lon slice
hght_850 = ds.Geopotential_height_isobaric.metpy.sel(
    vertical=level, lat=lat_slice, lon=lon_slice).squeeze().metpy.unit_array
tmpk_850 = ds.Temperature_isobaric.metpy.sel(
    vertical=level, lat=lat_slice, lon=lon_slice).squeeze().metpy.unit_array
uwnd_850 = ds['u-component_of_wind_isobaric'].metpy.sel(
    vertical=level, lat=lat_slice, lon=lon_slice).squeeze().metpy.unit_array
vwnd_850 = ds['v-component_of_wind_isobaric'].metpy.sel(
    vertical=level, lat=lat_slice, lon=lon_slice).squeeze().metpy.unit_array

# Convert temperatures to degree Celsius for plotting purposes
tmpc_850 = tmpk_850.to('degC')

# Get a sensible datetime format
"""
vtime = ds.time.data[0].astype('datetime64[ms]').astype('O')
"""
vtime = ds.time.data[t].astype('datetime64[ms]').astype('O')
# 時間スライスの追加
hght_850 = hght_850[t]
tmpk_850 = tmpk_850[t]
uwnd_850 = uwnd_850[t]
vwnd_850 = vwnd_850[t]
tmpc_850 = tmpc_850[t]

# 平滑化
hght_850 = ndimage.gaussian_filter(hght_850, sigma=3)
tmpc_850 = ndimage.gaussian_filter(tmpc_850, sigma=3)

######################################################################
# Figure Creation
# ---------------
#
# Here we use Cartopy to plot a CONUS map using a Lambert Conformal
# projection - note: the data is in a lat/lon projection, so the
# PlateCarree projection is used as the data projection.
#

# Set output projection
"""
mapcrs = ccrs.LambertConformal(
    central_longitude=-100, central_latitude=35, standard_parallels=(30, 60))
"""
mapcrs = ccrs.LambertConformal(central_longitude=(WEST+EAST)/2, central_latitude=(SOUTH+NORTH)/2,
                               standard_parallels=(30, 60))

# Set projection of data (so we can transform for the figure)
datacrs = ccrs.PlateCarree()

# Start figure and set extent to be over CONUS
fig = plt.figure(1, figsize=COM.FIGSIZE)
ax = plt.subplot(111, projection=mapcrs)
"""
ax.set_extent([-130, -72, 20, 55], ccrs.PlateCarree())
"""
ax.set_extent([WEST, EAST, SOUTH, NORTH], ccrs.PlateCarree())
ax.set_xmargin(0)
ax.set_ymargin(0)

# Add coastline and state map features
ax.add_feature(cfeature.COASTLINE.with_scale('50m'))
ax.add_feature(cfeature.STATES.with_scale('50m'))

# Plot colorfill and dashed contours of 850-hPa temperatures in Celsius
#clevs_850_tmpc = np.arange(-48, -15, 3)
#cf = ax.contourf(lons, lats, tmpc_850, clevs_850_tmpc, cmap=plt.cm.Blues_r, transform=datacrs)
clevs_850_tmpc = np.arange(-24-24, 24-24+1, 3)
cf = ax.contourf(lons, lats, tmpc_850, clevs_850_tmpc, cmap=plt.cm.coolwarm, transform=datacrs)
cb = plt.colorbar(cf, orientation='horizontal', pad=0, aspect=50, shrink=COM.SHRINK)
cb.set_label('Temperature (C)')
csf = ax.contour(lons, lats, tmpc_850, clevs_850_tmpc, colors='grey',linewidths=COM.LINEWIDTH,
                 linestyles='dashed', transform=datacrs)
plt.clabel(csf, fmt='%d',fontsize=COM.FONTSIZE)

# Plot contours of 850-hPa geopotential heights in meters
clevs_850_hght = np.arange(0, 8000, 60)
cs = ax.contour(lons, lats, hght_850, clevs_850_hght, colors='black', linewidths=COM.LINEWIDTH,
	transform=datacrs)
plt.clabel(cs, fmt='%d')

# Plot wind barbs every fifth element
wind_slice = (slice(None, None, 5), slice(None, None, 5))
ax.barbs(lons[wind_slice[0]], lats[wind_slice[1]],
         uwnd_850[wind_slice[0], wind_slice[1]].to('kt').m,
         vwnd_850[wind_slice[0], wind_slice[1]].to('kt').m,
         pivot='middle', color='black', transform=datacrs)

# Add some titles
"""
plt.title('GFS 500-hPa Geopotential Heights (m), Temperature (C), '
          'and Wind Barbs (kt)', loc='left')
plt.title('Valid Time: JST {}'.format(vtime+timedelta(hours=9)), loc='right')
plt.show()
"""
plt.title('GFS 500-hPa Heights (m), Temp. (C) and Wind Barbs (kt)', loc='left',fontsize=COM.FONTSIZE)
plt.title('JST {}'.format(vtime+timedelta(hours=9)), loc='right',fontsize=COM.FONTSIZE)
#
plt.subplots_adjust(left=COM.LEFT, right=COM.RIGHT, top=COM.TOP, bottom=COM.BOTTOM)
plt.savefig(OUT_PATH, transparent=COM.TRANSPARENT) #bbox_inches='tight',pad_inches=COM.PAD_INCHES)
# Close all
plt.close(fig)
ds.close()

