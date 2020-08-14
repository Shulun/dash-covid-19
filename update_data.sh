#!/bin/sh

PATH=/path/1:/path/2
PATH=/sbin:/usr/sbin/:/usr/local/sbin:/bin:/usr/local/bin

DATAFILE=/root/dash-covid-19/data/alltime_world.csv
NEWFILE=/root/dash-covid-19/data/alltime_world_copy.csv
/data/tools/Python3.6.2/bin/python3.6 /root/dash-covid-19/crawler.py
mv $NEWFILE $DATAFILE
