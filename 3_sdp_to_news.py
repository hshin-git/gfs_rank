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
print("enter:",sys.argv)
print("date:",datetime.now())
print("in1:",STAT_PATH)
print("in2:",DATA_PATH)
print("out:",OUT_PATH)
os.makedirs(OUT_PATH, exist_ok=True)


########################################################
## カテゴリ予報
CRAIN = 'Categorical_Rain_surface_00'
CSNOW = 'Categorical_Freezing_Rain_surface_00'
TCDC = 'Total_cloud_cover_boundary_layer_cloud_Mixed_intervals_Average_00'
REF_COLS = [CRAIN,CSNOW,TCDC]
## 天気の判別ルール
def TENKI(day):
  if day[CSNOW]>0.1:
    return "雪"
  elif day[CRAIN]>0.1:
    return "雨"
  elif day[TCDC]>80.0:
    return "曇"
  elif day[TCDC]>20.0:
    return "晴"
  else:
    return "快"

########################################################
## 出力データフレームの作成
NEWS = pd.DataFrame([],columns=["SDP","FUKEN","NAME","DATE",u"天気"])

#SDP_LIST = SDP_LIST[20:25]
for SDP in SDP_LIST.index[:]:
  FUKEN = SDP_LIST.loc[SDP,'FUKEN']
  NAME = SDP_LIST.loc[SDP,'NAME']
  print(NAME)
  ## 最新値
  DATA = pd.read_csv("%s/%05d.csv"%(DATA_PATH,SDP),parse_dates=[0],index_col=0)
  DATA = DATA[REF_COLS]
  DATA = DATA[1:]	# 1日8コマへ整列（前日21:00を落とす）
  ## 日毎の統計値を計算
  DATA = DATA.resample('1D').mean()
  ## 日毎の要約文を作成
  for d in DATA.index:
    avg = DATA.loc[d]
    tenki = TENKI(avg)
    row = pd.Series([SDP,FUKEN,NAME,d,tenki],index=NEWS.columns)
    NEWS = NEWS.append(row,ignore_index=True)
    print(d,NAME,tenki)
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
print("leave:",sys.argv)
sys.exit(0)

