#!/bin/bash

function AndroidPullData()
{
	local NAME=$1
	local DIR=$2
	local TAR_FILE=$NAME.tar.gz
	local LOCAL_FILE=data/$TAR_FILE
	local TEMP_FILE=/sdcard/$TAR_FILE
	adb shell "su -c 'tar czf $TEMP_FILE -C $DIR $NAME'" \
		&& adb pull $TEMP_FILE $LOCAL_FILE \
		&& adb shell "rm $TEMP_FILE"
}

function LocalUnTar()
{
	local NAME=$1
	local LOCAL_FILE=data/$NAME.tar.gz
	echo $LOCAL_FILE
	if [ -f $LOCAL_FILE ]; then
		tar zxf $LOCAL_FILE -C data
	fi
}

function LocalDelData()
{
	local LOCAL_PATH=data/$1
	if [ -d $LOCAL_PATH ]; then
		rm -rf $LOCAL_PATH
	fi
	if [ -f $LOCAL_PATH ]; then
		rm $LOCAL_PATH
	fi
}

