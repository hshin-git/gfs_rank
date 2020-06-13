# -*- coding: utf-8 -*-
import numpy  as np
import pandas as pd
import scipy.stats as stats
#import matplotlib.pyplot as plt
import os,sys
from datetime import datetime
import COMMON as COM

##################################################
## 抽出地点と気象変数の指定
ENCODE = "cp932"
SDP_LIST = pd.read_csv(COM.INFO_PATH +"/"+ "sdp_list.csv",index_col="SDP",encoding=ENCODE)

## ランキング計算の入力
# 以下のSTAT,DATA
STAT_PATH = COM.HCST_PATH	#"./hindcast"
DATA_PATH = COM.FCST_PATH	#"./forecast"

## ランキング結果の出力先
OUT_PATH = COM.INFO_PATH	#"./info"
print("enter:", sys.argv)
print("now:", datetime.now())
print("in1:", STAT_PATH)
print("in2:", DATA_PATH)
print("out:", OUT_PATH)
os.makedirs(OUT_PATH, exist_ok=True)


## 気象変数の単位
GFS_LIST = pd.read_csv(COM.INFO_PATH +"/"+ "gfs_list.csv",index_col="GFS")
UNITS = {}
for v in GFS_LIST.index:
  UNITS[v] = GFS_LIST.loc[v,"units"]


##################################################
## 統計値の読み込み
STAT = pd.read_csv(DATA_PATH +"/"+ "gfs_mean1d.csv")
FPCT = {}
FKDE = {}
for v in STAT.columns[1:]:
  # パーセンタイル値: p0,p1,...,p99,p100
  PCT = STAT.loc[3:103,v].values
  # PCT関数: GFS変数→パーセンタイル
  FPCT[v] = np.vectorize(lambda x,PCT=np.copy(PCT): np.searchsorted(PCT, x)/1.01)
  # KDE関数: GFS変数→確率
  n = STAT.loc[0,v]
  sig = STAT.loc[2,v]
  iqr = PCT[75] - PCT[25]
  h = 0.9*min(sig,iqr/1.34)/(n**0.2)	# optimal bandwidth for KDE
  if h == 0.:
    FKDE[v] = lambda x: 1.0
  else:
    FKDE[v] = np.vectorize(lambda x,PCT=np.copy(PCT),h=h: sig*np.mean(stats.norm.pdf(x,PCT,h)))
  # デバッグ用: KDE可視化
  """
  if v in ['v-component_of_wind_tropopause_00',]:
    import matplotlib.pyplot as plt
    x = np.linspace(PCT[0]-sig,PCT[100]+sig,100)
    y = FKDE[v](x)
    plt.figure()
    plt.title(v)
    plt.xlabel(v)
    plt.plot(x,y)
    plt.plot(PCT,np.linspace(0,0,101),marker="o")
    plt.grid()
    plt.show()
  """

##################################################
## ランキングの計算処理
RANK = pd.DataFrame([],columns=["SDP","NAME","DATE","GFS","PERCENTILE","LOG10KDE","AVG"])

## ランク計算パラメータ
P01,P99,KDE,EPS = 1.,99.,1e-4,1e-300

#SDP_LIST = SDP_LIST[20:25]
for SDP in SDP_LIST.index[:]:
  NAME = SDP_LIST.loc[SDP,'NAME']
  ##################################################
  ## 予報値
  DATA = pd.read_csv("%s/%05d.csv"%(DATA_PATH,SDP),parse_dates=[0],index_col=0)
  DATA = DATA[:-(len(DATA)%8)]	# 1日8コマに整列
  DATA = DATA.resample("1D").mean()
  for v in DATA.columns[1:]:
    if not(v in STAT.columns[1:]): continue
    VAL = DATA[v]
    # パーセンタイル値のスコア
    PCT = pd.Series(FPCT[v](VAL), index=DATA.index)
    # 確率密度分布関数のスコア
    LOG = pd.Series(-np.log10(FKDE[v](VAL)+EPS), index=DATA.index)
    # 両スコアからレア日を列挙
    COND = ((PCT<P01) | (PCT>P99)) & (LOG>-np.log10(KDE))
    for d in COND[COND].index:
      print(sys.argv[0], SDP,NAME,d,v,PCT[d],LOG[d],VAL[d])
      row = pd.Series([SDP,NAME,d,v,PCT[d],LOG[d],VAL[d]],index=RANK.columns)
      RANK = RANK.append(row, ignore_index=True)

##################################################
## 大小に振れる変数を除外
VARS = RANK.groupby(["GFS"]).mean()["PERCENTILE"] 
VARS = VARS[(VARS<P01) | (VARS>P99)]
RANK = RANK[[v in list(VARS.index) for v in RANK.GFS]]

## 事象リストの保存
RANK["units"] = RANK.apply(lambda x: UNITS[x["GFS"][:-3]],axis=1)
RANK = RANK.sort_values(["DATE","SDP","GFS"])
RANK = RANK[["DATE","SDP","NAME","GFS","AVG","units","PERCENTILE"]]
RANK.to_csv(OUT_PATH +"/"+ "gfs_rank.csv",encoding=ENCODE)

#sys.exit(0)
##################################################
## 集約ランキングの保存
SCORE = "SCORE"
RANK = RANK.rename(columns={"NAME":SCORE})

## 変数ランキング
vRANK = RANK.groupby(["GFS"]).agg({SCORE:'count','PERCENTILE':'mean','AVG':'mean','SDP':lambda x:set(x),'DATE':lambda x:set(x)})
vRANK = vRANK.sort_values([SCORE],ascending=[False])
vRANK = vRANK.reset_index()
vRANK["units"] = vRANK.apply(lambda x: UNITS[x["GFS"][:-3]],axis=1)
vRANK = vRANK[["GFS","SCORE","PERCENTILE","AVG","units","SDP","DATE"]]
vRANK = vRANK.rename(columns={"SDP":"#SDP"})
vRANK.to_csv(OUT_PATH +"/"+ "var_rank.csv",encoding=ENCODE)

## 地点ランキング
sRANK = RANK.groupby(["SDP"]).agg({SCORE:'count','DATE':lambda x:set(x),'GFS':lambda x:set(x)})
sRANK = sRANK.sort_values([SCORE],ascending=[False])
sRANK = sRANK.join(SDP_LIST[["FUKEN","NAME"]])
sRANK = sRANK.reset_index()
sRANK = sRANK[["SDP","SCORE","NAME","DATE","GFS"]]
sRANK = sRANK.rename(columns={"GFS":"#GFS"})
sRANK.to_csv(OUT_PATH +"/"+ "sdp_rank.csv",encoding=ENCODE)

## 日付ランキング
dRANK = RANK.groupby(["DATE"]).agg({SCORE:'count','SDP':lambda x:set(x),'GFS':lambda x:set(x)})
dRANK = dRANK.sort_values([SCORE],ascending=[False])
dRANK = dRANK.reset_index()
dRANK = dRANK[["DATE","SCORE","SDP","GFS"]]
dRANK = dRANK.rename(columns={"SDP":"#SDP","GFS":"#GFS"})
dRANK.to_csv(OUT_PATH +"/"+ "day_rank.csv",encoding=ENCODE)

##################################################
print("leave:", sys.argv)
sys.exit(0)

