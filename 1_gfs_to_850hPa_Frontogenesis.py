"""
850-hPa Geopotential Heights, Temperature, Frontogenesis, and Winds
===================================================================

Frontogenesis at 850-hPa with Geopotential Heights, Temperature, and
Winds

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
#import netCDF4
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

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import metpy.calc as mpcalc
from metpy.units import units
import numpy as np
import xarray as xr
plt.style.use(COM.MPLSTYLE)


######################################################################
# Use Xarray to access GFS data from THREDDS resource and uses
# metpy accessor to parse file to make it easy to pull data using
# common coordinate names (e.g., vertical) and attach units.
#
"""
ds = xr.open_dataset('https://thredds.ucar.edu/thredds/dodsC/casestudies/'
                     'python-gallery/GFS_20101026_1200.nc').metpy.parse_cf()
"""
ds = xr.open_dataset(GFS_PATH).metpy.parse_cf()

######################################################################
# Subset data based on latitude and longitude values, calculate potential
# temperature for frontogenesis calculation.
#

# Set subset slice for the geographic extent of data to limit download
lon_slice = slice(WEST, EAST)
lat_slice = slice(NORTH, SOUTH)

# Grab lat/lon values (GFS will be 1D)
lats = ds.lat.sel(lat=lat_slice).values
lons = ds.lon.sel(lon=lon_slice).values

level = 850 * units.hPa
hght_850 = ds.Geopotential_height_isobaric.metpy.sel(
    vertical=level, lat=lat_slice, lon=lon_slice).metpy.unit_array.squeeze()
tmpk_850 = ds.Temperature_isobaric.metpy.sel(
    vertical=level, lat=lat_slice, lon=lon_slice).metpy.unit_array.squeeze()
uwnd_850 = ds['u-component_of_wind_isobaric'].metpy.sel(
    vertical=level, lat=lat_slice, lon=lon_slice).metpy.unit_array.squeeze()
vwnd_850 = ds['v-component_of_wind_isobaric'].metpy.sel(
    vertical=level, lat=lat_slice, lon=lon_slice).metpy.unit_array.squeeze()

# Convert temperatures to degree Celsius for plotting purposes
tmpc_850 = tmpk_850.to('degC')

# Calculate potential temperature for frontogenesis calculation
thta_850 = mpcalc.potential_temperature(level, tmpk_850)

# Get a sensible datetime format
vtime = ds.time.data[t].astype('datetime64[ms]').astype('O')

# 時間スライスの追加
hght_850 = hght_850[t]
tmpk_850 = tmpk_850[t]
uwnd_850 = uwnd_850[t]
vwnd_850 = vwnd_850[t]
tmpc_850 = tmpc_850[t]
thta_850 = thta_850[t]


######################################################################
# Calculate frontogenesis
# -----------------------
#
# Frontogenesis calculation in MetPy requires temperature, wind
# components, and grid spacings. First compute the grid deltas using MetPy
# functionality, then put it all together in the frontogenesis function.
#
# Note: MetPy will give the output with SI units, but typically
# frontogenesis (read: GEMPAK) output this variable with units of K per
# 100 km per 3 h; a conversion factor is included here to use at plot time
# to reflect those units.
#

dx, dy = mpcalc.lat_lon_grid_deltas(lons, lats)

fronto_850 = mpcalc.frontogenesis(thta_850, uwnd_850, vwnd_850, dx, dy, dim_order='yx')

# A conversion factor to get frontogensis units of K per 100 km per 3 h
convert_to_per_100km_3h = 1000*100*3600*3


# 平滑化
from scipy.ndimage import gaussian_filter
SIGMA = 3.0/1.0
hght_850 = gaussian_filter(hght_850,sigma=SIGMA)
tmpc_850 = gaussian_filter(tmpc_850,sigma=SIGMA)
#fronto_850 = gaussian_filter(fronto_850,sigma=SIGMA)
#sys.exit(0)


######################################################################
# Plotting Frontogenesis
# ----------------------
#
# Using a Lambert Conformal projection from Cartopy to plot 850-hPa
# variables including frontogenesis.
#

# Set map projection
mapcrs = ccrs.LambertConformal(central_longitude=(WEST+EAST)/2, central_latitude=(SOUTH+NORTH)/2,
                               standard_parallels=(30, 60))
#mapcrs = ccrs.PlateCarree()

# Set projection of the data (GFS is lat/lon)
datacrs = ccrs.PlateCarree()

# Start figure and limit the graphical area extent
fig = plt.figure(1, figsize=COM.FIGSIZE)
ax = fig.add_subplot(111, projection=mapcrs)
ax.set_extent([WEST, EAST, SOUTH, NORTH], ccrs.PlateCarree())
ax.set_xmargin(0)
ax.set_ymargin(0)

# Add map features of Coastlines and States
ax.add_feature(cfeature.COASTLINE.with_scale('50m'))
ax.add_feature(cfeature.STATES.with_scale('50m'))

# Plot 850-hPa Frontogenesis
cf = ax.contourf(lons, lats, fronto_850*convert_to_per_100km_3h, np.arange(-8, 8.5, 0.5),
                 cmap=plt.cm.bwr, extend='both', transform=datacrs)
cb = plt.colorbar(cf, ax=ax, orientation='horizontal', pad=0, aspect=50, shrink=COM.SHRINK)
cb.set_label('Frontogenesis (K/100km/3h)')

# Plot 850-hPa Temperature in Celsius
clevs_tmpc = np.arange(-42, 42+1, 3)
csf = ax.contour(lons, lats, tmpc_850, clevs_tmpc, colors='tab:red',linewidths=COM.LINEWIDTH,
                 linestyles='dashed', transform=datacrs)
plt.clabel(csf, fmt='%d')

# Plot 850-hPa Geopotential Heights
clevs_850_hght = np.arange(0, 8000, 30)
cs = ax.contour(lons, lats, hght_850, clevs_850_hght, colors='black', linewidths=COM.LINEWIDTH,
		transform=datacrs)
plt.clabel(cs, fmt='%d')

# Plot 850-hPa Wind Barbs only plotting every fifth barb
wind_slice = (slice(None, None, 5), slice(None, None, 5))
ax.barbs(lons[wind_slice[0]], lats[wind_slice[1]],
         uwnd_850[wind_slice].to('kt').m, vwnd_850[wind_slice].to('kt').m,
         color='black', transform=datacrs)

# Plot some titles
"""
plt.title('GFS 850-hPa Geopotential Heights (m), Temp (C), and Winds', loc='left')
plt.title('Valid Time: JST {}'.format(vtime+timedelta(hours=9)), loc='right')
plt.show()
"""
plt.title('GFS 850-hPa Heights (m), Temp (C), and Winds', loc='left', fontsize=COM.FONTSIZE)
plt.title('JST {}'.format(vtime+timedelta(hours=9)), loc='right', fontsize=COM.FONTSIZE)
plt.savefig(OUT_PATH, transparent=COM.TRANSPARENT) #bbox_inches='tight',pad_inches=COM.PAD_INCHES)
# Close all
plt.close(fig)
ds.close()

