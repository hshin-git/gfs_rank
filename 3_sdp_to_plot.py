# -*- coding: utf-8 -*-
import matplotlib as mpl
mpl.use('Agg')
##
import numpy  as np
import pandas as pd
import matplotlib.pyplot as plt
import os,sys
from datetime import datetime
import COMMON as COM
##
plt.style.use(COM.MPLSTYLE)
plt.rcParams["font.family"] = "IPAexGothic"
plt.rcParams["font.sans-serif"] = "IPAexGothic"


########################################################
## GFSファイルからSDPリスト地点の気象量を抽出してCSV保存する
########################################################
## コマンドライン引数: SDPリスト
SDP_PLOT = sys.argv[1:]
CSV_PATH = COM.FCST_PATH	#"./forecast"
OUT_PATH = COM.PLOT_PATH	#"./graph"

print("argv:",sys.argv)
print("date:",datetime.now())
print("csv:",CSV_PATH)
print("out:",OUT_PATH)
os.makedirs(OUT_PATH, exist_ok=True)


########################################################
## 抽出地点と気象変数の指定
ENCODE = "cp932"
SDP_LIST = pd.read_csv("./info/sdp_list.csv",index_col="SDP",encoding=ENCODE)
SDP_PLOT = SDP_LIST.index if len(SDP_PLOT)==0 else SDP_PLOT


########################################################
#SDP_PLOT = SDP_PLOT[:2]
for SDP in SDP_PLOT:
  SDP = int(SDP)
  NAME = SDP_LIST.loc[SDP,"NAME"]
  FUKEN = SDP_LIST.loc[SDP,"FUKEN"]
  DF = pd.read_csv(CSV_PATH +"/"+ "%05d.csv"%SDP,parse_dates=[0],index_col=0)
  DF = DF[:-(len(DF)%8)]
  print(SDP,NAME)
  ########################################################
  ## データ準備
  ## 気温(degC)
  T0K = 273.15
  DF['TMP'] = DF['Temperature_surface_00'] - T0K
  DF['DPT'] = DF['Dewpoint_temperature_height_above_ground_00'] - 273.15
  ## 雲量(0-1)
  DF['TCDC'] = DF['Total_cloud_cover_entire_atmosphere_Mixed_intervals_Average_00'] / 100.
  DF['High'] = DF['Total_cloud_cover_high_cloud_Mixed_intervals_Average_00'] / 100.
  DF['Middle'] = DF['Total_cloud_cover_middle_cloud_Mixed_intervals_Average_00'] / 100.
  DF['Low'] = DF['Total_cloud_cover_low_cloud_Mixed_intervals_Average_00'] / 100.
  ## 天気(0-1)
  DF['CRAIN'] = DF['Categorical_Rain_surface_00']
  DF['CSNOW'] = DF['Categorical_Snow_surface_00']
  DF['CICEP'] = DF['Categorical_Ice_Pellets_surface_00']
  ## 大気放射(kW/m2)
  DF['LWD'] = DF['Downward_Long-Wave_Radp_Flux_surface_Mixed_intervals_Average_00'] / 1000.
  DF['SWD'] = DF['Downward_Short-Wave_Radiation_Flux_surface_Mixed_intervals_Average_00'] / 1000.
  ## 大気安定度(kJ/kg)
  DF['CAPE'] = DF['Convective_available_potential_energy_surface_00'] / 1000.
  DF['CIN'] = DF['Convective_inhibition_surface_00'] / 1000.
  ## 高層気温(degC) @ isobaric6=[0,3,6,9,...,33]
  """
  DF['T350mb'] = DF['Temperature_isobaric_18'] - T0K
  DF['T500mb'] = DF['Temperature_isobaric_21'] - T0K
  DF['T800mb'] = DF['Temperature_isobaric_27'] - T0K
  DF['T925mb'] = DF['Temperature_isobaric_30'] - T0K
  DF['T1000mb'] = DF['Temperature_isobaric_33'] - T0K
  """
  ## 視程(km)
  DF['VIS'] = DF['Visibility_surface_00'] / 1000.
  ## 突風(m/s)
  DF['GUST'] = DF['Wind_speed_gust_surface_00']
  ## リフト指数(K)
  DF['4LFTX'] = DF['Best_4_layer_Lifted_Index_surface_00']
  DF['LFTX'] = DF['Surface_Lifted_Index_surface_00']
  ## 湿度(%)
  DF['RH'] = DF['Relative_humidity_height_above_ground_00']
  ########################################################
  ## プロット作成
  #plt.ticklabel_format(useLocale=False)
  fig, axes = plt.subplots(nrows=6,ncols=1,figsize=(5,8))
  fig.suptitle('{0:05d} {1:} {2:} UTC {3}'.format(SDP,FUKEN,NAME,DF.reftime[0][:-3]))
  ## 気温(degC)
  row = 0
  for c in ['TMP','DPT']: DF[c].plot(ax=axes[row],label=c,marker='.',sharex=True)
  axes[row].set_ylabel("Temp. (C)")
  axes[row].grid(True)
  axes[row].legend(loc='right')
  ## 大気放射(kW/m2)
  row = row + 1
  for c in ['SWD','LWD']: DF[c].plot(ax=axes[row],label=c,marker='.',sharex=True)
  axes[row].set_ylabel("Flux (kW/m2)")
  axes[row].grid(True)
  axes[row].legend(loc='right')
  axes[row].set_ylim(0.0,1.05)
  ## 天気(0-1)
  row = row + 1
  for c in ['CRAIN','CSNOW','CICEP']: DF[c].plot(ax=axes[row],label=c,marker='.',sharex=True)
  axes[row].set_ylabel("Cat. (0-1)")
  axes[row].grid(True)
  axes[row].legend(loc='right')
  axes[row].set_ylim(0.0,1.05)
  ## 雲量(0-1)
  row = row + 1
  for c in ['TCDC','High','Middle','Low']: DF[c].plot(ax=axes[row],label=c,marker='.',sharex=True)
  axes[row].set_ylabel("Cloud (0-1)")
  axes[row].grid(True)
  axes[row].legend(loc='right')
  axes[row].set_ylim(0,1.05)
  ## 視程(km)
  row = row + 1
  for c in ['VIS']: DF[c].plot(ax=axes[row],label=c,marker='.',sharex=True)
  axes[row].set_ylabel("Visibility (km)")
  axes[row].grid(True)
  axes[row].legend(loc='right')
  axes[row].set_ylim(0,30)
  ## 高層気温(degC)
  """
  row = row + 1
  for c in ['T800mb','T500mb','T350mb']: DF[c].plot(ax=axes[row],label=c,marker='.',sharex=True)
  axes[row].set_ylabel("Temp. (C)")
  axes[row].grid(True)
  axes[row].legend(loc='right')
  #axes[row].set_ylim(-2,2)
  """
  ## 大気安定度(kJ/kg)
  """
  row = row + 1
  for c in ['CAPE','CIN']: DF[c].plot(ax=axes[row],label=c,marker='.',sharex=True)
  axes[row].set_ylabel("Stability (kJ/kg)")
  axes[row].grid(True)
  axes[row].legend(loc='right')
  #axes[row].set_ylim(-2,2)
  """
  ## 大気安定度(K)
  row = row + 1
  for c in ['4LFTX','LFTX']: DF[c].plot(ax=axes[row],label=c,marker='.',sharex=True)
  axes[row].set_ylabel("Stability (K)")
  axes[row].grid(True)
  axes[row].legend(loc='right')
  #axes[row].set_ylim(-2,2)
  ########################################################
  ## PNG保存
  plt.savefig(OUT_PATH +"/"+ "%05d.png"%SDP, transparent=COM.TRANSPARENT)
  #plt.savefig(OUT_PATH +"/"+ "%05d.svg"%SDP)
  plt.close(fig)
  ## CSV保存: イマココ用
  #DF = DF[["TMP","DPT","SWD","LWD","CRAIN","CSNOW","CICEP","TCDC","VIS","GUST"]]
  DF["TNK"] = DF.apply(lambda x: (u"雪" if x.CSNOW else (u"雨" if x.CRAIN else (u"曇" if x.TCDC>0.8 else (u"晴" if x.TCDC>0.2 else u"快")))), axis=1)
  COL = {"TNK":u"天気","TMP":u"気温","RH":u"湿度","TCDC":u"雲量","SWD":u"日射","GUST":u"突風","VIS":u"視程"}
  DF = DF[list(COL)]
  DF = DF.rename(columns=COL)
  DF.to_csv(OUT_PATH +"/"+ "%05d.csv"%SDP, encoding=ENCODE)

## JSON保存: イマココ用
SDP_LIST = SDP_LIST.reset_index()
SDP_LIST.to_json(OUT_PATH +"/"+ "sdp_list.json")

########################################################
sys.exit(0)

