# Copyright (c) 2017 MetPy Developers.
# Distributed under the terms of the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause
"""
Four Panel Map
===============

By reading model output data from a netCDF file, we can create a four panel plot showing:

* 300 hPa heights and winds
* 500 hPa heights and absolute vorticity
* Surface temperatures
* Precipitable water
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



###########################################
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as ndimage
import xarray as xr
import sys

from metpy.cbook import get_test_data
from metpy.plots import add_metpy_logo

###########################################
#crs = ccrs.LambertConformal(central_longitude=(WEST+EAST)/2., central_latitude=(SOUTH+NORTH)/2.)
crs = ccrs.PlateCarree()

###########################################
# Function used to create the map subplots
def plot_background(ax):
    #ax.set_extent([235., 290., 20., 55.])
    ax.set_extent([WEST, EAST, SOUTH, NORTH])
    ax.set_xmargin(0)
    ax.set_ymargin(0)
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.5)
    ax.add_feature(cfeature.STATES, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    return ax

###########################################
# Open the example netCDF data
"""
ds = xr.open_dataset(get_test_data('gfs_output.nc', False))
print(ds)
"""
ds = xr.open_dataset(GFS_PATH)


###########################################
# Combine 1D latitude and longitudes into a 2D grid of locations
lon_2d, lat_2d = np.meshgrid(ds['lon'], ds['lat'])

# time
vtime = ds.time.data[t].astype('datetime64[ms]').astype('O')
rtime = ds.reftime.data[t].astype('datetime64[ms]').astype('O')
#sys.exit(0)

###########################################
# Pull out the data
"""
vort_500 = ds['vort_500'][0]
surface_temp = ds['temp'][0]
precip_water = ds['precip_water'][0]
winds_300 = ds['winds_300'][0]
"""
iso_300 = np.where(ds.variables['isobaric'][:] == 300*100)[0][0]
iso2_500 = np.where(ds.variables['isobaric2'][:] == 500*100)[0][0]

vort_500 = ds.variables['Absolute_vorticity_isobaric'][t, iso2_500, :, :] 
surface_temp = ds['Temperature_surface'][t]
precip_water = ds['Precipitable_water_entire_atmosphere_single_layer'][t]
ucomp_300 = ds['u-component_of_wind_isobaric'][t, iso_300, :, :] 
vcomp_300 = ds['v-component_of_wind_isobaric'][t, iso_300, :, :] 
winds_300 = np.sqrt(ucomp_300**2 + vcomp_300**2)

###########################################
# Do unit conversions to what we wish to plot
vort_500 = vort_500 * 1e5
"""
surface_temp.metpy.convert_units('degF')
precip_water.metpy.convert_units('inches')
"""
surface_temp = surface_temp - 273.15	# K => degC
precip_water = precip_water	# 1 kg/m2 => 1 mm
winds_300 = winds_300 / 1.94384	# m/s => knots

###########################################
# Smooth the height data
"""
heights_300 = ndimage.gaussian_filter(ds['heights_300'][0], sigma=1.5, order=0)
heights_500 = ndimage.gaussian_filter(ds['heights_500'][0], sigma=1.5, order=0)
"""
iso6_300 = np.where(ds.variables['isobaric6'][:] == 300*100)[0][0]
iso6_500 = np.where(ds.variables['isobaric6'][:] == 500*100)[0][0]
heights_300 = ds['Geopotential_height_isobaric'][t, iso6_300, :, :]
heights_500 = ds['Geopotential_height_isobaric'][t, iso6_500, :, :]
heights_300 = ndimage.gaussian_filter(heights_300, sigma=1.5, order=0)
heights_500 = ndimage.gaussian_filter(heights_500, sigma=1.5, order=0)

#sys.exit(0)
###########################################
# Create the figure and plot background on different axes
fig, axarr = plt.subplots(nrows=2, ncols=2, figsize=COM.FIGSIZE, #constrained_layout=True,
                          subplot_kw={'projection': crs})
#add_metpy_logo(fig, 140, 120, size='large')
axlist = axarr.flatten()
for ax in axlist:
    plot_background(ax)

# Upper left plot - 300-hPa winds and geopotential heights
cf1 = axlist[0].contourf(lon_2d, lat_2d, winds_300, cmap='cool', transform=ccrs.PlateCarree())
c1 = axlist[0].contour(lon_2d, lat_2d, heights_300, colors='black', linewidths=1,
                       transform=ccrs.PlateCarree())
axlist[0].clabel(c1, fontsize=10, inline=1, inline_spacing=1, fmt='%i', rightside_up=True)
axlist[0].set_title('300-hPa Wind Speeds (kt) and Heights (m)')#, fontsize=16)
cb1 = fig.colorbar(cf1, ax=axlist[0], orientation='horizontal', shrink=0.5, pad=0)
cb1.set_label('kt')#, size='x-large')

# Upper right plot - 500mb absolute vorticity and geopotential heights
cf2 = axlist[1].contourf(lon_2d, lat_2d, vort_500, cmap='BrBG', transform=ccrs.PlateCarree(),
                         zorder=0, norm=plt.Normalize(-32, 32))
c2 = axlist[1].contour(lon_2d, lat_2d, heights_500, colors='k', linewidths=1,
                       transform=ccrs.PlateCarree())
axlist[1].clabel(c2, fontsize=10, inline=1, inline_spacing=1, fmt='%i', rightside_up=True)
axlist[1].set_title('500-hPa Absolute Vorticity and Heights (m)')#, fontsize=16)
cb2 = fig.colorbar(cf2, ax=axlist[1], orientation='horizontal', shrink=0.5, pad=0)
cb2.set_label(r'$10^{-5}$ s$^{-1}$')#, size='x-large')

# Lower left plot - surface temperatures
cf3 = axlist[2].contourf(lon_2d, lat_2d, surface_temp, cmap='YlOrRd',
                         transform=ccrs.PlateCarree(), zorder=0)
axlist[2].set_title('Surface Temperatures (degC)')#, fontsize=16)
cb3 = fig.colorbar(cf3, ax=axlist[2], orientation='horizontal', shrink=0.5, pad=0)
cb3.set_label(u'\N{DEGREE CELSIUS}')#, size='x-large')

# Lower right plot - precipitable water entire atmosphere
cf4 = axlist[3].contourf(lon_2d, lat_2d, precip_water, cmap='Greens',
                         transform=ccrs.PlateCarree(), zorder=0)
axlist[3].set_title('Precipitable Water (mm)')#, fontsize=16)
cb4 = fig.colorbar(cf4, ax=axlist[3], orientation='horizontal', shrink=0.5, pad=0)
cb4.set_label('mm')#, size='x-large')

# Set height padding for plots
fig.set_constrained_layout_pads(w_pad=0., h_pad=0., hspace=0., wspace=0.)

# Set figure title
#fig.suptitle(ds['time'][t].dt.strftime('%Y-%m-%d %H:%MZ').values, fontsize=16)
fig.suptitle('GFS Forecast for JST {}'.format(vtime+timedelta(hours=9)) + ' at UTC {}'.format(rtime), fontsize=COM.FONTSIZE)

# Display the plot
#plt.show()
plt.savefig(OUT_PATH, transparent=COM.TRANSPARENT) #bbox_inches='tight',pad_inches=COM.PAD_INCHES)
# Close all
plt.close(fig)
ds.close()

