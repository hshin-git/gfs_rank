#!/bin/sh

#DEBUG=echo 
echo $DEBUG

echo "##################################################"
$DEBUG rm ./forecast/*.csv

echo "##################################################"
#$DEBUG rm ./hindcast/*.csv

echo "##################################################"
$DEBUG rm ./chart/*.png
$DEBUG rm ./graph/*.png
$DEBUG rm ./tile/*.png
$DEBUG rm ./info/*.csv
$DEBUG rm ./info/*.html

