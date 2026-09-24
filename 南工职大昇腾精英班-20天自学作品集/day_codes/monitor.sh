#!/bin/bash
while true
do
  echo "== $(date +%T) ==" >> ~/project/log/report.log
  free -m | grep Mem >> ~/project/log/report.log
  top -b -n 1 | grep Cpu >> ~/project/log/report.log
  sleep 2
done
