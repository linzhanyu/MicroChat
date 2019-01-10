#!/bin/bash

source shell/base.sh

USER_HASH=$1
DIR=/sdcard/tencent/MicroMsg/$USER_HASH

names=(voice2 )
for name in ${names[@]}
do
	echo $DIR/$name
	AndroidPullData $name $DIR
	if [ $? -eq 0 ]; then
		LocalDelData $name
		LocalUnTar $name
	fi
done

