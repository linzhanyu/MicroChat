#!/bin/bash

SKIL=thirdpart/silk-v3-decoder/converter.sh
INPUT_AMR=$1
echo `pwd`
bash $SKIL $INPUT_AMR mp3
echo ${INPUT_AMR%.*}.mp3

