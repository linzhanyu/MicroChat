#!/bin/bash

# EnMicroMsg.db
source shell/base.sh
USER_HASH=$1
NAME=EnMicroMsg.db
DIR=/data/data/com.tencent.mm/MicroMsg/$USER_HASH

AndroidPullData $NAME $DIR
LocalUnTar $NAME

