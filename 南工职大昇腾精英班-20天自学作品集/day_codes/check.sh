#!/bin/bash
code=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8080)
if [ "$code" = "200" ]; then
  echo "服务正常"
else
  echo "服务异常"
fi
