## 出力先のパラメータ
DATA_PATH = "./gfs"
CONF_PATH = "./conf"
INFO_PATH = "./info"
FCST_PATH = "./forecast"
HCST_PATH = "./hindcast"
CHRT_PATH = "./chart"
TILE_PATH = "./tile"
PLOT_PATH = "./graph"

## 時刻のパラメータ
GFS_INIT = 12
GFS_DAYS = 7
CSV_TIME = 'JST'
CSV_ZONE = 9

## グラフのパラメータ
MPLSTYLE='default'
#MPLSTYLE = 'dark_background'
#MPLSTYLE = 'bmh'
#MPLSTYLE = 'fivethirtyeight'
#MPLSTYLE = 'ggplot'
#MPLSTYLE = 'seaborn-dark'

## 天気図のパラメータ
AREA = [115,155,20+0,50]	# WEST,EAST,SOUTH,NORTH
FIGSIZE = (12,10)
SHRINK = 0.9
LINEWIDTH = 2
FONTSIZE = 16
TRANSPARENT = True
#PAD_INCHES = 1
LEFT = 0.0
RIGHT = 1.0
BOTTOM = -0.05
TOP = 0.95

