# -*- coding: utf-8 -*-
import numpy  as np
import pandas as pd
#import matplotlib.pyplot as plt
import os,sys,re
from datetime import datetime
import COMMON as COM


##################################################
CSV_LIST = sys.argv[1:]
print("argv:",sys.argv)
print("date:",datetime.now())

##################################################
ENCODE = "cp932"

HEADER = '''
<html lang="ja">
<head>
<meta charset="utf-8">
<title>dataframe</title>
<link rel="stylesheet" href="../common.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/datatables/1.10.20/css/jquery.dataTables.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/lightbox2/2.7.1/css/lightbox.css" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/datatables/1.10.20/js/jquery.dataTables.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/lightbox2/2.7.1/js/lightbox.min.js"></script>
<script> $(document).ready( function () { $('.dataframe').DataTable({ "scrollX":true, "stateSave":true, "order":[], }); } ); </script>
</head>
<body>
'''

FOOTER = '''
</body>
</html>
'''

##################################################
## 天気テキスト
TENKI_COLOR = {	#色付き文字
  u"快":"<font color=#f00>{}</font>",
  u"晴":"<font color=#f00>{}</font>",
  u"曇":"<font color=#000>{}</font>",
  u"雨":"<font color=#00f>{}</font>",
  u"雪":"<font color=#0f0>{}</font>",
}
TENKI_EMOJI = {	#絵文字
  u"快":"&#x1f31e;",
  u"晴":"&#x1f324;",
  u"曇":"&#x2601;",
  u"雨":"&#x1f327;",
  u"雪":"&#x1f328;",
}
TENKI_ICONS = {	#画像（いらすとや）
  u"快":"<img id='tenki' src='../tenki/hare.png' alt='快'>",
  u"晴":"<img id='tenki' src='../tenki/hare_kumori.png' alt='晴'>",
  u"曇":"<img id='tenki' src='../tenki/kumori.png' alt='曇'>",
  u"雨":"<img id='tenki' src='../tenki/kumori_ame.png' alt='雨'>",
  u"雪":"<img id='tenki' src='../tenki/snow.png' alt='雪'>",
}

## ヘルパ関数
def _NORMALIZE(s): return re.sub(r'_[0-9]{2}',"",s.replace("'","").replace("Timestamp(","").replace(" 00:00:00)","").replace(" ",""))
def _SETtoLIST(s): return s.replace("{","").replace("}","").split(",")
def _MAPandJOIN(fn,ls): return "<br>".join([fn(x) for x in ls])
def _GFS_HREF(s): return "<a href='../tile/{0}.png' data-lightbox='{0}'>{0}</a>".format(s)
def _GFS_HREF1(s): return "<a id='{0}' href='./gfs_list.html#{0}'>{0}</a>".format(s)
def _GFS_HREF2(s): return "<a id='{0}' href='./var_rank.html#{0}'>{0}</a> {1}".format(s,VAR_TEXT[s])
def _SDP_HREF(s): return "<a href='../graph/{0}.png' data-lightbox='{0}'>{0}</a>".format(s)
def _JST_PID(s): return "<p id='{0}'>{1}</p>".format(s[:-6].replace("-","").replace(" ",""),s[:-3]) 
#def _ICONIFY(s): return TENKI_COLOR[s[0]].format(s) if s[0] in TENKI_COLOR else s
#def _ICONIFY(s): return TENKI_EMOJI[s[0]] if s[0] in TENKI_EMOJI else s
def _ICONIFY(s): return TENKI_ICONS[s[0]] if s[0] in TENKI_ICONS else s

## フォーマット関数
FORMATTERS = {
  "JST": lambda x: _JST_PID(x),
  "SDP": lambda x: _SDP_HREF(x),
  "GFS": lambda x: _GFS_HREF(x),
#"GFS": lambda x: _MAPandJOIN(_GFS_HREF,sorted(_SETtoLIST(_NORMALIZE(x)))),
#"#GFS": lambda x: _MAPandJOIN(_GFS_HREF2,sorted(_SETtoLIST(_NORMALIZE(x)))),
#"#SDP": lambda x: _MAPandJOIN(_SDP_HREF,sorted(_SETtoLIST(_NORMALIZE(x)))),
  "DATE": lambda x: _MAPandJOIN(lambda x:x, sorted(_SETtoLIST(_NORMALIZE(x)))),
  "天気":_ICONIFY,
  "月":_ICONIFY, "火":_ICONIFY, "水":_ICONIFY, "木":_ICONIFY, "金":_ICONIFY, "土":_ICONIFY, "日":_ICONIFY,
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
  ## format csv
  CSV = pd.read_csv(src,encoding=ENCODE)
  COLS = [c for c in CSV.columns if not c.startswith("Unnamed:")]
  CSV = CSV[COLS]
  ## format html
  html = HEADER
  html += CSV.to_html(index_names=False,
		table_id=name,
		float_format="%.1f",
		formatters=FORMATTERS,
		render_links=True,
		escape=False,
		index=False,
		show_dimensions=False,
		classes="compact row-border stripe",
		border=0)
  html += FOOTER
  ## write html
  with open(dst,'w') as f:
    f.write(html)
    f.close()

##################################################
sys.exit(0)

