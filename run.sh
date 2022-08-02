#!/bin/bash

PID=$(netstat -nlp | grep 5001 | awk '{print $7}' | awk -F '[ / ]' '{print $1}')
if [ $PID ]; then
        echo "kill process id is:${PID}"
        kill -9 ${PID}
fi
#python3 main.py 
nohup python3 main.py  > logs.txt 2>&1 &
