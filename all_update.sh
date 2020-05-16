#!/bin/bash
echo "BEGIN:" $(date)
#DEBUG=echo
PYTHON=/home/shin/anaconda3/bin/python
#PYTHON=/home/ubuntu/anaconda3/bin/python


echo "##################################################"
##### 年月日の計算: 起動日前日UTC12時=JST21時の初期値を利用
#GFS_INIT="2020042812"
GFS_INIT=$(date "+%Y%m%d12" -d "-1 days")
GFS_PATH="gfs/gfs_"${GFS_INIT}"_168.nc"

GFS_PAST=$(date "+%Y%m%d12" -d "-28 days")
DAY_WEEK=$(date "+%w")

echo "gfs_init:" $GFS_INIT
echo "gfs_path:" $GFS_PATH
echo "gfs_past:" $GFS_PAST
echo "day_week:" $DAY_WEEK


echo "##################################################"
##### SDPリストの作成: conf/ame_*.csv -> info/sdp_list.csv
$DEBUG $PYTHON 0_ame_to_list.py conf/ame_master.csv

echo "##################################################"
##### GFSデータの取得: THREDD Server -> gfs/gfs_*.nc
$DEBUG $PYTHON 0_tds_to_gfs.py $GFS_INIT

echo "##################################################"
##### GFS変数表の作成: gfs/gfs_*.nc -> info/gfs_list.csv
$DEBUG $PYTHON 1_gfs_to_list.py $GFS_PATH

echo "##################################################"
##### SDP統計値の作成: conf/*.csv, gfs/gfs_*.nc -> forecast/*.csv
$DEBUG $PYTHON 2_gfs_to_stat.py

echo "##################################################"
##### GFSランクの作成: conf/*.csv, (forecast|hindcast)/*.csv -> info/gfs_rank*.csv
$DEBUG $PYTHON 3_gfs_to_rank.py

echo "##################################################"
##### SDP予報文の作成: conf/*.csv, (forecast|hindcast)/*.csv -> info/sdp_news*.csv
$DEBUG $PYTHON 3_sdp_to_news.py

echo "##################################################"
##### SDPグラフの作成: conf/*.csv, forecast/*.csv -> tile/*.png
$DEBUG $PYTHON 3_sdp_to_plot.py

echo "##################################################"
##### HTML文書の作成: info/*.csv -> info/*.html
$DEBUG $PYTHON 4_csv_to_html.py ./info/*.csv ./graph/*.csv
#exit


echo "##################################################"
##### GFS天気図の作成: gfs/gfs_*.nc -> chart/*.png
for t in `seq 0 2 56`
do
  echo chart $t
  ##### Surface
  $PYTHON 1_gfs_to_Surface_HILO_Symbol.py $GFS_PATH $t
  ##### 850hPa
  #$PYTHON 1_gfs_to_850hPa_Frontogenesis.py $GFS_PATH $t
  #$PYTHON 1_gfs_to_850hPa_TMPC_Winds.py $GFS_PATH $t
  $PYTHON 1_gfs_to_850hPa_Temperature_Advection.py $GFS_PATH $t
  ##### 700hPa
  $PYTHON 1_gfs_to_700hPa_RELH_Winds.py $GFS_PATH $t
  ##### 500hPa
  $PYTHON 1_gfs_to_500hPa_HGHT_Winds.py $GFS_PATH $t
  #$PYTHON 1_gfs_to_500hPa_TMPC_Winds.py $GFS_PATH $t
  #$PYTHON 1_gfs_to_500hPa_Vorticity_Advection.py $GFS_PATH $t
  ##### 300hPa
  $PYTHON 1_gfs_to_300hPa_HGHT_Winds.py $GFS_PATH $t
  ##### other
  #$PYTHON 1_gfs_to_MetPy_Four_Panel_Map.py $GFS_PATH $t
done

echo "##################################################"
##### GFSタイルの作成: conf/*.csv, gfs/gfs_.nc -> tile/*.png
#$PYTHON 2_gfs_to_tile.py $GFS_PATH Visibility_surface


echo "##################################################"
##### 定期メンテナンス処理
## CSVファイルの保存: info/*.csv, forecast/*.csv -> data/*.zip
$DEBUG zip ./data/${GFS_INIT}.zip info/*.csv forecast/*.csv

## CSVファイルの更新: conf/*.csv, gfs/gfs_*.nc -> hindcast/*.csv
if [ $DAY_WEEK = 0 ]; then 
$DEBUG $PYTHON 2_gfs_to_stat.py $GFS_PAST $GFS_INIT 7
fi

## GFSファイルの削除: gfs/gfs_old.nc -> null
for p in $(seq 1 1 14); do
OUT_DATE=$(date "+%Y%m%d12" -d "${GFS_PAST:0:-2} -$p days")
gfs="./gfs/gfs_${OUT_DATE}_168.nc"
if [ -e $gfs ]; then
$DEBUG rm $gfs
fi
done


echo "##################################################"
echo "END:" $(date)
exit 0

