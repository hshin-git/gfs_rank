"""
===========================
500 hPa Vorticity Advection
===========================

Plot an 500-hPa map with calculating vorticity advection using MetPy calculations.

Beyond just plotting 500-hPa level data, this uses calculations from `metpy.calc` to find
the vorticity and vorticity advection. Currently, this needs an extra helper function to
calculate the distance between lat/lon grid points.
"""
######################################################################
import matplotlib as mpl
mpl.use('Agg')
import os,sys
from datetime import timedelta
import netCDF4
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


########################################
# Imports
from datetime import datetime

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.gridspec as gridspec
import matplotlib.pylab as plt
import metpy.calc as mpcalc
from metpy.units import units
from netCDF4 import num2date
import numpy as np
import scipy.ndimage as ndimage
from siphon.ncss import NCSS
plt.style.use(COM.MPLSTYLE)


#######################################
# Data Aquisition
# ---------------
"""
# Open the example netCDF data
ncss = NCSS('https://www.ncei.noaa.gov/thredds/ncss/grid/namanl/'
            '201604/20160416/namanl_218_20160416_1800_000.grb')
now = datetime.utcnow()

# Query for Latest GFS Run
hgt = ncss.query().time(datetime(2016, 4, 16, 18)).accept('netcdf')
hgt.variables('Geopotential_height_isobaric', 'u-component_of_wind_isobaric',
              'v-component_of_wind_isobaric').add_lonlat()

# Actually getting the data
ds = ncss.get_data(hgt)
"""
ds =  netCDF4.Dataset(GFS_PATH, 'r')

#lon = ds.variables['lon'][:]
#lat = ds.variables['lat'][:]
lon, lat = np.meshgrid(ds['lon'], ds['lat'])

times = ds.variables[ds.variables['Temperature_surface'].dimensions[0]]
vtime = num2date(times[:], units=times.units)


lev_500 = np.where(ds.variables['isobaric'][:] == 500*100)[0][0]
lev6_500 = np.where(ds.variables['isobaric6'][:] == 500*100)[0][0]

hght_500 = ds.variables['Geopotential_height_isobaric'][t, lev6_500, :, :]
hght_500 = ndimage.gaussian_filter(hght_500, sigma=3, order=0) #* units.meter

uwnd_500 = ds.variables['u-component_of_wind_isobaric'][t, lev_500, :, :]
vwnd_500 = ds.variables['v-component_of_wind_isobaric'][t, lev_500, :, :]


#######################################
# Begin Data Calculations
# -----------------------

dx, dy = mpcalc.lat_lon_grid_deltas(lon, lat)

f = mpcalc.coriolis_parameter(np.deg2rad(lat))

#avor = mpcalc.vorticity(uwnd_500, vwnd_500, dx, dy, dim_order='yx') + f
# use gfs's avor (absolute vorticity)
lev2_500 = np.where(ds.variables['isobaric2'][:] == 500*100)[0][0]
avor = ds.variables['Absolute_vorticity_isobaric'][t, lev2_500, :, :] + f.m

avor = ndimage.gaussian_filter(avor, sigma=3, order=0)

vort_adv = mpcalc.advection(avor, [uwnd_500, vwnd_500], (dx, dy), dim_order='yx')

#sys.exit(0)
#######################################
# Map Creation
# ------------

# Set up Coordinate System for Plot and Transforms
"""
dproj = ds.variables['LambertConformal_Projection']
globe = ccrs.Globe(ellipse='sphere', semimajor_axis=dproj.earth_radius,
                   semiminor_axis=dproj.earth_radius)
datacrs = ccrs.LambertConformal(central_latitude=dproj.latitude_of_projection_origin,
                                central_longitude=dproj.longitude_of_central_meridian,
                                standard_parallels=[dproj.standard_parallel],
                                globe=globe)
plotcrs = ccrs.LambertConformal(central_latitude=45., central_longitude=-100.,
                                standard_parallels=[30, 60])

fig = plt.figure(1, figsize=(14., 12))

gs = gridspec.GridSpec(2, 1, height_ratios=[1, .02], bottom=.07, top=.99,
                       hspace=0.01, wspace=0.01)
ax = plt.subplot(gs[0], projection=plotcrs)
"""
plotcrs = ccrs.LambertConformal(central_longitude=(WEST+EAST)/2, central_latitude=(SOUTH+NORTH)/2,
                               standard_parallels=(30, 60))
datacrs = ccrs.PlateCarree()
fig = plt.figure(1, figsize=COM.FIGSIZE)
ax = plt.subplot(111, projection=plotcrs)
ax.set_xmargin(0)
ax.set_ymargin(0)


# Plot Titles
"""
plt.title(r'GFS 500-hPa Heights (m), AVOR$*10^5$ ($s^{-1}$), AVOR Adv$*10^9$ ($s^{-2}$)',
          loc='left')
plt.title('Valid Time: JST {}'.format(vtime[t]+timedelta(hours=9)), loc='right')
"""
plt.title(r'GFS 500-hPa Heights (m), AVOR$*10^5$ ($s^{-1}$), AVOR Adv$*10^9$ ($s^{-2}$)', loc='left', fontsize=COM.FONTSIZE)
plt.title('JST {}'.format(vtime[t]+timedelta(hours=9)), loc='right', fontsize=COM.FONTSIZE)

# Plot Background
#ax.set_extent([235., 290., 20., 58.], ccrs.PlateCarree())
ax.set_extent([WEST, EAST, SOUTH, NORTH], ccrs.PlateCarree())
ax.coastlines('50m', edgecolor='black', linewidth=0.75)
ax.add_feature(cfeature.STATES, linewidth=.5)

# Plot Height Contours
clev500 = np.arange(5100, 6061, 60)
cs = ax.contour(lon, lat, hght_500, clev500, colors='black', linewidths=COM.LINEWIDTH,
                linestyles='solid', transform=ccrs.PlateCarree())
plt.clabel(cs, fontsize=COM.FONTSIZE,
	inline=1, inline_spacing=10, fmt='%i', rightside_up=True, use_clabeltext=True)

# Plot Absolute Vorticity Contours
clevvort500 = np.arange(-10, 50, 5)
cs2 = ax.contour(lon, lat, avor*10**5, clevvort500, colors='tab:red', linewidths=COM.LINEWIDTH,
	linestyles='dashed', transform=ccrs.PlateCarree())
plt.clabel(cs2, fontsize=COM.FONTSIZE,
	inline=1, inline_spacing=10, fmt='%i', rightside_up=True, use_clabeltext=True)
"""
clevvort500 = np.arange(0, 400+1, 40)
cs2 = ax.contour(lon, lat, (avor-f.m)*10e5, clevvort500, colors='grey',
                 linewidths=2.0, linestyles='dashed', transform=ccrs.PlateCarree())
plt.clabel(cs2, fontsize=10, inline=1, inline_spacing=10, fmt='%i',
           rightside_up=True, use_clabeltext=True)
"""

# Plot Colorfill of Vorticity Advection
clev_avoradv = np.arange(-18, 18+1, 3)
cf = ax.contourf(lon, lat, vort_adv.m * 1e9, clev_avoradv[clev_avoradv != 0], #extend='both',
                 cmap='bwr', transform=ccrs.PlateCarree())
#cax = plt.subplot(gs[1])
#cb = plt.colorbar(cf, orientation='horizontal', extendrect='True', ticks=clev_avoradv)
cb = plt.colorbar(cf, orientation='horizontal', pad=0, aspect=50, ticks=clev_avoradv, shrink=COM.SHRINK)
cb.set_label(r'Absolute Vorticity Advection ($1/s^2$)')


# Plot Wind Barbs
# Transform Vectors and plot wind barbs.
#ax.barbs(lon, lat, uwnd_500, vwnd_500, length=6, regrid_shape=20,
#         pivot='middle', transform=ccrs.PlateCarree())
KT = 1.94384
ax.barbs(lon, lat, uwnd_500*KT, vwnd_500*KT, pivot='middle', color='grey',
	regrid_shape=20, transform=ccrs.PlateCarree())

#plt.show()
plt.savefig(OUT_PATH, transparent=COM.TRANSPARENT) #bbox_inches='tight',pad_inches=COM.PAD_INCHES)
# Close all
plt.close(fig)
ds.close()

