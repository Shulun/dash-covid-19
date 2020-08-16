#! /bin/bash

str=$"\n"
pid=$(ps -ef | grep "python /root/dash-covid-19/app.py" | grep -v grep | awk '{print $2}' )
kill 9 $pid
nohup python /root/dash-covid-19/app.py &
sstr=$(echo -e $str)
echo $sstr