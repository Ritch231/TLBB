FROM python:3.10.11-slim-buster

RUN pip3 install requests
RUN pip3 install lxml
# 创建工作文件夹
RUN mkdir -p /workfolder
RUN mkdir -p /workfolder/app
RUN mkdir -p /workfolder/app/config
RUN mkdir -p /workfolder/config/logs
RUN mkdir -p /workfolder/config/logs/log_bbs
RUN mkdir -p /workfolder/config/logs/log_server
# 设置工作目录
WORKDIR /workfolder
# 复制 Python 文件到容器中
COPY ./app/server.py /workfolder/app/server.py
COPY ./app/bbs.py /workfolder/app/bbs.py
COPY ./app/config/config.json /workfolder/app/config/config.json
# 复制启动脚本到容器中
COPY start.sh /workfolder/start.sh
# 设置启动脚本的可执行权限
RUN chmod +x start.sh

# CMD [ "python", "/workfolder/TLBB_loginserver.py"]

# 指定容器启动时执行的命令
CMD ["./start.sh"]