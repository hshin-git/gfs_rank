# -*- coding: utf-8 -*-
import numpy  as np
import pandas as pd
#import matplotlib.pyplot as plt
import os,sys
from datetime import datetime
import COMMON as COM

##################################################
## 気象庁アメダス一覧
JMA_LIST = sys.argv[1] if len(sys.argv) > 1 else "./conf/ame_master.csv"
OUT_PATH = COM.INFO_PATH	#"./info"
##
print("argv:",sys.argv)
print("date:",datetime.now())
print("csv:",JMA_LIST)
print("out:",OUT_PATH)
os.makedirs(OUT_PATH, exist_ok=True)

##################################################
ENCODE = "cp932"
DF = pd.read_csv(JMA_LIST,encoding=ENCODE)

## カラム名の変換
COLS = {
	u"都府県振興局":"FUKEN",
	u"観測所番号":"SDP",
	u"種類":"TYPE",
	u"観測所名":"NAME",
	u"所在地":"LOCATION",
	u"緯度(度)":"LATdeg",
	u"緯度(分)":"LATmin",
	u"経度(度)":"LONdeg",
	u"経度(分)":"LONmin",
	u"海面上の高さ(ｍ)":"SDPm",
	u"風速計の高さ(ｍ)":"WINm",
	u"温度計の高さ(ｍ)":"TMPm"
}
DF = DF[COLS]
DF = DF.rename(columns=COLS)

## 気象官署に限定
DF = DF[DF.TYPE==u"官"]
DF = DF.drop_duplicates(subset="SDP")

## 気象台に限定
DF = DF[DF.LOCATION.str.contains(u"気象台")]

## 緯度、経度の変換
ROUND = 3
DF["lat"] = np.round(DF.LATdeg + DF.LATmin/60., decimals=ROUND)
DF["lon"] = np.round(DF.LONdeg + DF.LONmin/60., decimals=ROUND)

## CSV保存
DF.to_csv(OUT_PATH +"/"+ "sdp_list.csv",index=False,encoding=ENCODE)

##################################################
sys.exit(0)

