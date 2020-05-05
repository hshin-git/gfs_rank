# -*- coding: utf-8 -*-
import numpy  as np
import pandas as pd
#import matplotlib.pyplot as plt
import os,sys
from datetime import datetime
import COMMON as COM


##################################################
CSV_LIST = sys.argv[1:]
print("argv:",sys.argv)

##################################################
ENCODE = "cp932"

HEADER = '''
<link rel="stylesheet" type="text/css" href="../common.css">
'''

FOOTER = '''
<p>This document was created at JST {}.</p>
'''

##################################################
## GFS変数のアドホック処理
VAR_RANK = pd.read_csv("./info/var_rank.csv")
VAR_TEXT = {}
for i in VAR_RANK.index:
  v = VAR_RANK.loc[i,"GFS"][:-3]
  p = VAR_RANK.loc[i,"PERCENTILE"]
  if p > 75:
    VAR_TEXT[v] = "is large."
  elif p < 25:
    VAR_TEXT[v] = "is small."
  else:
    VAR_TEXT[v] = "is unknown."

##################################################
## 天気テキスト
TENKI_COLOR = {
  u"快":"<font color=#f00>{}</font>",
  u"晴":"<font color=#f00>{}</font>",
  u"曇":"<font color=#000>{}</font>",
  u"雨":"<font color=#00f>{}</font>",
  u"雪":"<font color=#0f0>{}</font>",
}
TENKI_EMOJI = {
  u"快":"&#x1f31e;",
  u"晴":"&#x1f324;",
  u"曇":"&#x2601;",
  u"雨":"&#x1f327;",
  u"雪":"&#x1f328;",
}

## ヘルパ関数
def _NORMALIZE(s): return s.replace("'","").replace("Timestamp(","").replace(" 00:00:00)","").replace("_00","").replace(" ","")
def _SETtoLIST(s): return s.replace("{","").replace("}","").split(",")
def _MAPandJOIN(fn,ls): return "<br>".join([fn(x) for x in ls])
def _GFS_HREF(s): return "<a id='{0}' href='./gfs_list.html#{0}'>{0}</a>".format(s)
def _GFS_HREF2(s): return "<a id='{0}' href='./var_rank.html#{0}'>{0}</a> {1}".format(s,VAR_TEXT[s])
def _SDP_HREF(s): return "<a href='../graph/{0}.png'>{0}</a>".format(s)
def _ICONIFY(s): return TENKI_COLOR[s[0]].format(s) if s[0] in TENKI_COLOR else s
def _ICONIFY(s): return TENKI_EMOJI[s[0]] if s[0] in TENKI_EMOJI else s
def _JST_PID(s): return "<p id='{0}'>{1}</p>".format(s[:-6].replace("-","").replace(" ",""),s[:-3]) 

## フォーマット関数
FORMATTERS = {
  "JST": lambda x: _JST_PID(x),
  "SDP": lambda x: _SDP_HREF(x), 
  "GFS": lambda x: _MAPandJOIN(_GFS_HREF,sorted(_SETtoLIST(_NORMALIZE(x)))),
  "#GFS": lambda x: _MAPandJOIN(_GFS_HREF2,sorted(_SETtoLIST(_NORMALIZE(x)))),
  "DATE": lambda x: _MAPandJOIN(lambda x:x, sorted(_SETtoLIST(_NORMALIZE(x)))),
  u"天気":_ICONIFY,
  u"月":_ICONIFY, u"火":_ICONIFY, u"水":_ICONIFY, u"木":_ICONIFY, u"金":_ICONIFY, u"土":_ICONIFY, u"日":_ICONIFY,
}

## 出力時の長さ制限なし
pd.set_option('display.max_colwidth', -1)

##################################################
for src in CSV_LIST:
  ## src -> dst
  path,base = os.path.split(src)
  name,ext = os.path.splitext(base)
  dst = path +"/"+ name +".html"
  print(path,base,name,ext,dst)
  ##
  CSV = pd.read_csv(src,encoding=ENCODE)
  COLS = [c for c in CSV.columns if not c.startswith("Unnamed:")]
  CSV = CSV[COLS]
  ##
  with open(dst,'w') as f:
    f.write(
	HEADER
	+ CSV.to_html(index_names=False,
		table_id=name,
		float_format="%.1f",
		formatters=FORMATTERS,
		render_links=True,
		escape=False,
		show_dimensions=True,
		border=0)
	+ FOOTER.format(datetime.now())
	)

##################################################
sys.exit(0)

