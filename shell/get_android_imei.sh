#!/bin/bash
# 取IMEI

# IMEI1
adb shell service call iphonesubinfo 3 | awk -F "'" '{print $2}' | sed '1 d' | tr -d '.' | awk '{print}' ORS=
echo 
# IMEI2
adb shell service call iphonesubinfo 1 | awk -F "'" '{print $2}' | sed '1 d' | tr -d '.' | awk '{print}' ORS=
echo 

