FROM python:3.10.11-slim-buster

RUN pip3 install requests
# 创建工作文件夹
RUN mkdir -p /workfolder
# 复制 Python 文件到容器中
COPY ./src/TLBB_loginserver.py /workfolder/TLBB_loginserver.py
COPY ./src/tlbbs.py /workfolder/tlbbs.py
# 复制启动脚本到容器中
COPY start.sh /workfolder/start.sh
# 设置工作目录
WORKDIR /workfolder
# 设置启动脚本的可执行权限
RUN chmod +x start.sh

# CMD [ "python", "/workfolder/TLBB_loginserver.py"]

# 指定容器启动时执行的命令
CMD ["./start.sh"]