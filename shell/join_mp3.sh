#!/bin/bash

ffmpeg -i "concat:$1" -acodec copy data/$2.mp3
echo data/$2.mp3

