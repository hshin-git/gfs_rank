#!/bin/sh

#DEBUG=echo 
echo $DEBUG

echo "##################################################"
$DEBUG rm ./forecast/*.csv

echo "##################################################"
#$DEBUG rm ./hindcast/*.csv

echo "##################################################"
$DEBUG rm ./chart/*.png
$DEBUG rm ./graph/*.png ./graph/*.csv ./graph/*.html 
$DEBUG rm ./info/*.csv ./info/*.html
$DEBUG rm ./tile/*.png
