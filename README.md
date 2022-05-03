# gfs_rank

![Surface_015](https://tenki.cf/gfs/chart/Surface_HILO_Symbol_015.png)


## 概説
サイト[GFS Rank](http://tenki.cf/gfs/)は、全球予報GFS（水平解像度0.5度）にもとづく天気図とランキングを掲載する。 それぞれの特徴は「天気図を前後上下ボタンで切り替えられる点」と「気象量の珍しさをランキングする点」である。 コンテンツは、21時JST（12時UTC）初期値のGFSデータにもとづき毎朝に更新する。 


## 内容
### 天気図
日本周辺（緯度:20〜50度、経度:120〜150度）の地表面および気圧面（850,700,500,300hPa面）に関する天気図である。 特徴は、すべての天気図を水平位置が重なるように作図し、前後上下をボタンで切り替えて大気状態を観察できる点にある。 地表天気図は、低気圧および高気圧のシンボル表示、平均海面気圧、降水域の表示を含む。 高層天気図は、気温、風、高度場の表示に加えて、気圧面により温度移流域、湿潤域や強風域を含む。 たとえば地表の降水域に対して、高層の温度移流や高度場との対応を参照することで、低気圧の鉛直構造を観察できる。


### 地点予報
代表地点（全国62地点）における一週間の天気概要である。各地点における気象量の時系列図も参照できまる。 気象量の時系列は、地上付近の気温や露点温度（℃）、地表面への短波と長波の放射強度（kW/m2）、雲量（%）、視程（km）などを含む。


### 注目変数
予報期間内の気象変数の珍しさに関するランキングである。 ランキングは、直近の統計値を基準にしたレア事象の発生件数にもとづき作成する。 レア事象の定義は「GFSデータを気象変数毎にパーセンタイル値へ変換した上で、 地点および日毎の平均パーセンタイル値が1以下または99以上となる事象」である。 日々変化するランキング結果と天気実況との対応を観察することにより、 気象変数の意味および気象現象への理解が深まる（ことを意図した）。


## 参考
- [GFS Rank](http://tenki.cf/gfs/)
- [Global Forecast System - NOAA](https://data.nodc.noaa.gov/cgi-bin/iso?id=gov.noaa.ncdc:C00634)
- [MetPy - Unidata](https://unidata.github.io/MetPy/latest/index.html)
- [Siphon - Unidata](https://unidata.github.io/siphon/latest/index.html)
- [Anaconda](https://www.anaconda.com/products/individual)
