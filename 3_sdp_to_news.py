# -*- coding: utf-8 -*-
import numpy  as np
import pandas as pd
import scipy.stats as stats
#import matplotlib.pyplot as plt
import os,sys
from datetime import datetime
import COMMON as COM

########################################################
## SDPリスト地点のCSVファイルからカテゴリ予報を作成する
########################################################
## 抽出地点と気象変数の指定
ENCODE = "cp932"
SDP_LIST = pd.read_csv(COM.INFO_PATH +"/"+ "sdp_list.csv",index_col="SDP",encoding=ENCODE)

## カテゴリ予報の入力
# 以下のSTAT,DATA
STAT_PATH = COM.HCST_PATH	#"./hindcast"
DATA_PATH = COM.FCST_PATH	#"./forecast"

## カテゴリ予報の出力先
OUT_PATH = COM.INFO_PATH	#"./info"
print("argv:",sys.argv)
print("date:",datetime.now())
print("in1:",STAT_PATH)
print("in2:",DATA_PATH)
print("out:",OUT_PATH)
os.makedirs(OUT_PATH, exist_ok=True)


########################################################
## カテゴリ予報の対象変数
IDENT = lambda x: x
GFS_DICT = {
  ## GFS変数名: {'jpn':変数名,'vthr':[絶対閾値,...],'pthr':[相対閾値,...],'jcat':[カテゴリ名,...],'conv':[変換関数,単位]}
  'Categorical_Rain_surface':	{'jpn':u"降水",'vthr':[20,50],'jcat':[u"無",u"短",u"長"],'conv':[lambda x:x*100.,'%']},
  'Categorical_Snow_surface':	{'jpn':u"降雪",'vthr':[10,50],'jcat':[u"無",u"短",u"長"],'conv':[lambda x:x*100.,'%']},
  'Wind_speed_gust_surface':	{'jpn':u"突風",'pthr':[25,75],'jcat':[u"弱",u"並",u"強"],'conv':[IDENT,'m/s']},
  'Temperature_surface':	{'jpn':u"気温",'pthr':[25,75],'jcat':[u"低",u"並",u"高"],'conv':[lambda x:x-273.15,'C']},
  'Relative_humidity_height_above_ground':{'jpn':u"湿度",'pthr':[25,75],'jcat':[u"低",u"並",u"高"],'conv':[IDENT,'%']},
  'Total_cloud_cover_entire_atmosphere_Mixed_intervals_Average':{'jpn':u"雲量",'vthr':[20,80],'jcat':[u"快",u"晴",u"曇"],'conv':[IDENT,'%']},
  'Visibility_surface':		{'jpn':u"視程",'pthr':[25,75],'jcat':[u"悪",u"並",u"良"],'conv':[lambda x:x/1000.,'km']},
#  'Sunshine_Duration_surface':{'jpn':u"日照時間"},
#  'Dewpoint_temperature_height_above_ground':{'jpn':"露点温度"},
#  'Precipitable_water_entire_atmosphere_single_layer':{'jpn':u"可降水量"},
#  'Total_cloud_cover_high_cloud_Mixed_intervals_Average':{'jpn':u"高層雲量"},
#  'Total_cloud_cover_middle_cloud_Mixed_intervals_Average':{'jpn':u"中層雲量"},
#  'Total_cloud_cover_low_cloud_Mixed_intervals_Average':{'jpn':u"低層雲量"},
#  'Total_ozone_entire_atmosphere_single_layer':{'jpn':u"オゾン量"},
}
########################################################
## 数値予報からカテゴリ予報へ: 気象要素ごと
def JPN_CATEGORY(DAY,GFS_COL):
  JPN_ROW = []
  for v in GFS_COL:
    DICT = GFS_DICT[v]
    v0 =  v + "_00"
    jpn = DICT['jpn']
    ##
    unit = ""
    conv = lambda x: x
    conv = DICT['conv'][0] if 'conv' in DICT else conv
    unit = DICT['conv'][1] if 'conv' in DICT else unit
    ref = ":%.f%s" % (conv(DAY[v0]),unit)
    ## カテゴリ閾値の設定
    if 'vthr' in DICT:
      # 絶対値
      val = conv(DAY[v0])
      thr = DICT['vthr']
      cat = DICT['jcat']
    elif 'pthr' in DICT:
      # 相対値
      val = DAY[v]
      thr = DICT['pthr']
      cat = DICT['jcat']
    ## カテゴリ値へ
    ret = cat[len(thr)]
    for n in range(0,len(thr)):
      if val < thr[n]:
        ret = cat[n]
        break
    JPN_ROW += [ret+ref]
    #print(v,val,thr)
  return JPN_ROW

## 数値予報からカテゴリ予報へ: 最終的な天気
def JPN_SUMMARY(DAY):
  CLOUD,RAIN,SNOW = JPN_CATEGORY(DAY,[
	'Total_cloud_cover_entire_atmosphere_Mixed_intervals_Average',
	'Categorical_Rain_surface',
	'Categorical_Snow_surface'])
  ret = CLOUD[0]
  if not SNOW.startswith(u"無"):
    ret = u"雪"
  elif not RAIN.startswith(u"無"):
    ret = u"雨"
  return ret

########################################################
## 出力カテゴリの定義: 前記GFS_DICTに含まれる変数
NEWS_GFS = [
	'Temperature_surface',
	'Relative_humidity_height_above_ground',
	'Wind_speed_gust_surface',
	'Categorical_Rain_surface',
	'Categorical_Snow_surface',
	'Total_cloud_cover_entire_atmosphere_Mixed_intervals_Average',
	'Visibility_surface'
]
## 出力データフレームの作成
NEWS_JPN = [GFS_DICT[v]['jpn'] for v in NEWS_GFS]
NEWS = pd.DataFrame([],columns=["SDP","FUKEN","NAME","DATE",u"天気"]+NEWS_JPN)

#SDP_LIST = SDP_LIST[20:25]
for SDP in SDP_LIST.index[:]:
  FUKEN = SDP_LIST.loc[SDP,'FUKEN']
  NAME = SDP_LIST.loc[SDP,'NAME']
  print(NAME)
  ## 統計値
  STAT = pd.read_csv("%s/%05d_stat.csv"%(STAT_PATH,SDP))
  PCTL = {}
  REF_COLS = []
  for v in GFS_DICT:
    v0 = "%s_00"%v
    REF_COLS += [v0]
    # パーセンタイル変換(気象要素数値→パーセンタイル値[0-100])
    PCTL[v] = np.vectorize(lambda x: np.searchsorted(STAT.loc[3:103,v0].values, x))
  ## 最新値
  DATA = pd.read_csv("%s/%05d.csv"%(DATA_PATH,SDP),parse_dates=[0],index_col=0)
  DATA = DATA[REF_COLS]
  #DATA = DATA.dropna()
  DATA = DATA[:-(len(DATA)%8)]	# 1日8コマへ整列
  ## 気象量を相対値に変換
  for v in GFS_DICT:
    v0 = "%s_00"%v
    DATA[v] = PCTL[v](DATA[v0])
  ## 日毎の統計値を計算
  AVG = DATA.resample('1D').mean()
  ## 日毎の要約文を作成
  for d in AVG.index:
    avg = AVG.loc[d]
    tenki_cat = JPN_SUMMARY(avg)
    items_cat = JPN_CATEGORY(avg,NEWS_GFS)
    row = pd.Series([SDP,FUKEN,NAME,d]+[tenki_cat]+items_cat,index=NEWS.columns)
    NEWS = NEWS.append(row,ignore_index=True)
    print(d,NAME,tenki_cat,items_cat)
  ##

########################################################
## カテゴリ予報の保存
NEWS.to_csv(OUT_PATH +"/"+ "sdp_news.csv",encoding=ENCODE,index=False)


########################################################
## 週間予報表の整形: SDPxDAY
JDoW = [u"月",u"火",u"水",u"木",u"金",u"土",u"日"]
NROW = len(SDP_LIST)
NDAY = len(NEWS)//NROW

# 列データ
SDPs = SDP_LIST.index.tolist()
FUKs = SDP_LIST["FUKEN"].tolist()
NAMs = SDP_LIST["NAME"].tolist()
if NDAY <= 7:
  DAYs = NEWS["DATE"][0:NDAY].apply(lambda x:JDoW[x.dayofweek]).values.tolist()
else: #見やすい曜日カラムは、予報が1週間を超えるとカラム名が重複
  DAYs = NEWS["DATE"][0:NDAY].apply(lambda x:"%02d-%02d(%s)"%(x.month,x.day,JDoW[x.dayofweek])).values.tolist()
#NEWS[u"天気"] = NEWS.apply(lambda x: u"%s (%s)"%(x[u"天気"],x[u"気温"]), axis=1)
VALs = NEWS[u"天気"].values[0:NROW*NDAY].reshape(NROW,NDAY).T
VALS = np.vstack([SDPs,FUKs,NAMs,VALs])

# 列ヘッダ
COLS = ["SDP","FUKEN","NAME"] + DAYs

## 週間予報表の保存
WEEK = pd.DataFrame(VALS.T,columns=COLS)
WEEK.to_csv(OUT_PATH +"/"+ "sdp_week.csv",encoding=ENCODE,index=False)

########################################################
sys.exit(0)

