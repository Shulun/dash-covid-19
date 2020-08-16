#! /bin/bash

pid=$(ps -ef | grep "python app.py" | grep -v grep | awk '{print $2}' )
kill 9 $pid
nohup python /root/dash-covid-19/app.py &