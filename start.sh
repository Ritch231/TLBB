#!/bin/bash

# 在启动脚本中同时执行两个 Python 文件
python ./app/server.py &
python ./app/bbs.py &

# 这个脚本将保持运行，以保持容器处于活动状态
while true; do
    sleep 1
done
