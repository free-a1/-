#!/bin/bash
LOG=$1
total=$(wc -l < $LOG)
err=$(grep -c "ERROR" $LOG)
echo "总行数:$total 错误数:$err"
