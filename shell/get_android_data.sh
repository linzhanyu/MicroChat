#!/bin/bash

# 取IMEI
# IMEI1
adb shell service call iphonesubinfo 3 | awk -F "'" '{print $2}' | sed '1 d' | tr -d '.' | awk '{print}' ORS=
# IMEI2
adb shell service call iphonesubinfo 1 | awk -F "'" '{print $2}' | sed '1 d' | tr -d '.' | awk '{print}' ORS=
# UNI
adb pull /data/data/com.tencent.mm/shared_prefs/auth_info_key_prefs.xml

# 1. 列语音目录
cd /sdcard/tencent/MicroMsg
find -name voice2
# 2. 列帐户目录
su
cd /data/data/com.tencent.mm/
# 2. 打包语音到 sdcard
# 3. 打包帐户信息到
