#!/bin/sh
#google-chrome --allow-file-access-from-files ./index.html

# test for date
TODAY=$(date "+%Y%m%d12")
YESTERDAY=$(date "+%Y%m%d12" -d "-1 days")
DOW=$(date "+%w")

echo $TODAY $YESTERDAY $DOW
if [ $DOW = 7 ]; then
echo "today is sunday"
fi

# test for backup
for src in $(ls ./info/*.csv); do
dst="../info_history/"${TODAY}"-"$(basename $src)
echo cp $src $dst 
done

# test for backuping csv files
echo zip ./data/${TODAY}.zip ./info/*.csv　./graph/*.csv

# test for removing gfs files
for p in $(seq 15 1 30); do
PAST=$(date "+%Y%m%d12" -d "-$p days")
gfs="../gfs/gfs_${PAST}_168.nc"
if [ -e $gfs ]; then
echo rm $gfs
fi
done

