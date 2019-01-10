#!/bin/bash

source shell/base.sh

USER_HASH=$1
DIR=/data/data/com.tencent.mm/MicroMsg/$USER_HASH
# avatar
names=(avatar )
for name in ${names[@]}
do
	echo $DIR/$name
	AndroidPullData $name $DIR
	if [ $? -eq 0 ]; then
		LocalDelData $name
		LocalUnTar $name
	fi
done

