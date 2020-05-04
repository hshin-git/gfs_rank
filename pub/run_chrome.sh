#!/bin/sh
#google-chrome --allow-file-access-from-files ./index.html

# test date
TODAY=$(date "+%Y%m%d12")
YESTERDAY=$(date "+%Y%m%d12" -d "-1 days")
DOW=$(date "+%w")

echo $TODAY $YESTERDAY $DOW
if [ $DOW = 7 ]; then
echo "today is sunday"
fi

# test for
for src in $(ls ./info/*.csv); do
dst="../info_history/"${TODAY}"-"$(basename $src)
echo cp $src $dst 
done

