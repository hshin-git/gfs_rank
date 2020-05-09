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
print("argv:",sys.argv)
print("date:",datetime.now())
print("in1:",STAT_PATH)
print("in2:",DATA_PATH)
print("out:",OUT_PATH)
os.makedirs(OUT_PATH, exist_ok=True)


## 気象変数の単位
GFS_LIST = pd.read_csv(COM.INFO_PATH +"/"+ "gfs_list.csv",index_col="GFS")
UNITS = {}
for v in GFS_LIST.index:
  UNITS[v] = GFS_LIST.loc[v,"units"]


##################################################
## ランキングの計算処理
RANK = pd.DataFrame([],columns=["SDP","NAME","DATE","GFS","PERCENTILE","LOG10_PROB","MIN","AVG","MAX"])

#SDP_LIST = SDP_LIST[20:25]
for SDP in SDP_LIST.index[:]:
  NAME = SDP_LIST.loc[SDP,'NAME']
  ##################################################
  ## 統計値
  STAT = pd.read_csv("%s/%05d_stat.csv"%(STAT_PATH,SDP))
  FPCT = {}
  FKDE = {}
  for v in STAT.columns[1:]:
    # パーセンタイル値: p0,p1,...,p99,p100
    PCT = STAT.loc[3:103,v].values
    # PCT関数: 数値→パーセンタイル
    FPCT[v] = np.vectorize(lambda x: np.searchsorted(PCT, x)/1.01)
    # KDE関数: 数値→確率
    n = STAT.loc[0,v]
    sig = STAT.loc[2,v]
    iqr = PCT[75] - PCT[25]
    h = 0.9*min(sig,iqr/1.34)/(n**0.2)	# optimal bandwidth for KDE
    if h == 0.:
      FKDE[v] = lambda x: 1.0
    else:
      FKDE[v] = np.vectorize(lambda x: sig*np.mean(stats.norm.pdf(x,PCT,h)))
    # デバッグ用: KDE可視化
    """
    x = np.linspace(PCT[v][0]-sig,PCT[v][100]+sig,100)
    y = KDE[v](x)
    plt.figure()
    plt.title(SDP)
    plt.xlabel(v)
    plt.plot(x,y)
    plt.plot(PCT[v],np.linspace(0,0,101),marker="o")
    plt.grid()
    plt.show()
    """
  ##################################################
  ## 最新値
  DATA = pd.read_csv("%s/%05d.csv"%(DATA_PATH,SDP),parse_dates=[0],index_col=0)
  DATA = DATA[:-(len(DATA)%8)]	# 1日8コマに整列
  #DATA = DATA.dropna()
  for v in DATA.columns[1:]:
    if not(v in STAT.columns[1:]): continue
    VAL = DATA[v]
    # パーセンタイル値へ変換
    PCT = pd.Series(FPCT[v](VAL), index=DATA.index)
    PCT = PCT.resample('1D').mean()
    # 経験的確率分布KDEに基づくスコア
    LOG = pd.Series(-np.log10(FKDE[v](VAL)+1e-300), index=DATA.index)
    LOG = LOG.resample('1D').mean()
    # 統計値
    MIN = VAL.resample('1D').min()
    AVG = VAL.resample('1D').mean()
    MAX = VAL.resample('1D').max()
    # 日毎平均スコアの大きな日を列挙
    COND = ((PCT>99.) | (PCT<1.)) & (LOG>-np.log10(1e-20))
    #COND = (LOG>-np.log10(1e-50))
    for d in COND[COND].index:
      print(SDP,NAME,d,v,PCT[d],LOG[d],MIN[d],AVG[d],MAX[d])
      row = pd.Series([SDP,NAME,d,v,PCT[d],LOG[d],MIN[d],AVG[d],MAX[d]],index=RANK.columns)
      RANK = RANK.append(row,ignore_index=True)

##################################################
## 事象ランキングの保存
RANK = RANK.sort_values(["SDP","DATE","GFS"])
RANK.to_csv(OUT_PATH +"/"+ "gfs_rank.csv",encoding=ENCODE)

#sys.exit(0)
##################################################
## 集約ランキングの保存
SCORE = "SCORE"
RANK = RANK.rename(columns={"NAME":SCORE})

## 変数ランキング
vRANK = RANK.groupby(["GFS"]).agg({SCORE:'count','PERCENTILE':'mean','AVG':'mean','SDP':lambda x:len(set(x)),'DATE':lambda x:set(x)})
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
sRANK = sRANK[["SDP","SCORE","FUKEN","NAME","DATE","GFS"]]
sRANK = sRANK.rename(columns={"GFS":"#GFS"})
sRANK.to_csv(OUT_PATH +"/"+ "sdp_rank.csv",encoding=ENCODE)

## 日付ランキング
dRANK = RANK.groupby(["DATE"]).agg({SCORE:'count','SDP':lambda x:len(set(x)),'GFS':lambda x:set(x)})
dRANK = dRANK.sort_values([SCORE],ascending=[False])
dRANK = dRANK.reset_index()
dRANK = dRANK[["DATE","SCORE","SDP","GFS"]]
dRANK = dRANK.rename(columns={"SDP":"#SDP","GFS":"#GFS"})
dRANK.to_csv(OUT_PATH +"/"+ "day_rank.csv",encoding=ENCODE)

##################################################
sys.exit(0)

