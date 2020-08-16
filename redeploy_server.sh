#!/bin/bash
str=$"\n"
pid=$(ps -ef | grep "python3.6" | grep -v grep | awk '{print $2}')
kill 9 $pid
nohup /data/tools/Python3.6.2/bin/python3.6 /root/dash-covid-19/app.py >/root/dash-covid-19/nohup.out 2>&1 &
sstr=$(echo -e $str)
echo $sstr
