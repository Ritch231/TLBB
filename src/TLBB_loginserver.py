import datetime
import json
import logging
import os
import re
import socket
import time
from logging.handlers import TimedRotatingFileHandler

import requests

# 设置日志目录和文件名格式
# log_dir = '/workfolder/logs/loginserver'
log_dir = '/Users/vicen/code/loginserver'

# 创建日志目录（如果不存在）
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

'''
    用于向tg推送消息
    MESSAGE：发送消息的内容
    IsProxy：是否使用代理，1使用 0不使用
'''


def send_telegram_message(MESSAGE, IsProxy):
    # 机器人的 token
    TOKEN = '2122878220:AAHVc1j3r3bfIPfb9Hmqtw3OZNFVUcbTMaw'
    # TOKEN = '1773760234:AAHGJG-6v9LOd1ah_O5ou7_lHmK5SWvBlhw'
    # 聊天的 ID
    CHAT_ID = '-1001887080842'
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    json = {
        "chat_id": CHAT_ID,
        "text": MESSAGE
    }
    proxies = {
        "http": "http://192.168.60.2:7890",
        "https": "http://192.168.60.2:7890"
    }
    if IsProxy == 1:
        r = requests.post(url, json=json, proxies=proxies)
    else:
        r = requests.post(url, json=json)


'''
    向synology chat发送消息
'''


def send_chat_message(chat_text):
    api_url = "https://nas.evannas.top:446/webapi/entry.cgi"
    api_token = "sE4JWC9DJ8UGtaf7G5Lph82g7uSKw5WAoVsBTgTnOYs1T3MJbfPhSASebYtZVK7T"
    # 创建API请求的payload
    payload = {
        "api": "SYNO.Chat.External",
        "method": "incoming",
        "version": "2",
        "token": api_token,
        "payload": json.dumps({"text": chat_text})
    }
    # 发送POST请求
    response = requests.post(api_url, data=payload)


def check_server_information():
    # 端口状态，port_status=0端口关闭，port_status=1端口开放
    port_status = 0
    # 服务器状态:默认设置爆满
    server_status = "0"
    # 服务器版本号
    version = ""

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    url = 'http://tlbblmupdate.changyou.com/xtlbbclose-jd/loginserver.txt'

    # 设置检测周期30秒
    check_time = 30
    while True:
        # 获取当前日期
        today_date = datetime.date.today()
        # 构建日志文件名，格式为YYYYMMDD.log
        log_filename = today_date.strftime("%Y%m%d") + ".log"
        # 配置日志
        log = logging.getLogger("my_logger")
        log.setLevel(logging.INFO)

        # 每天创建一个新的日志文件，保留7天的日志
        handler = TimedRotatingFileHandler(
            os.path.join(log_dir, log_filename), when="midnight", interval=1, backupCount=7
        )

        # 设置日志格式
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)

        log.addHandler(handler)

        # 发送get请求
        responses = requests.get(headers=headers, url=url)
        # 连接服务器正常
        if responses.status_code == 200:
            # 设置编码格式
            responses.encoding = 'gb18030'
            text = responses.text
            # 正则匹配需要的参数（1,9031,4,0,0）第2个参数：服务器id 第3个参数：服务器状态（10=隐藏 4=维护 3=极好 2=繁忙 1=拥挤 0=爆满）
            # 双线-内测服务器,龙腾天下,1,9031,4,0,0,欢迎进入天龙内测服服务器,124.222.196.144:3733,124.222.196.144:3733,124.222.196.144:3733,124.222.196.144:3733,2,15,3.69.8153,0,0,0,0,0,0,0,0,0,0,0
            pattern = r'龙腾天下,(\d+),(\d+),(\d+),(\d+),(\d+),欢迎进入天龙内测服服务器,(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+).*?(\d+\.\d+\.\d+),'

            # 使用findall方法查找所有匹配的IP地址和端口号
            matches = re.findall(pattern, text)
            print(matches)
            if len(matches) > 0:
                if len(matches[0]) == 8:
                    log.info(
                        "ip:" + matches[0][5] + ":" + matches[0][6] + " 游戏版本号：" + matches[0][7] + " 服务器状态：" +
                        matches[0][2] + "  检测周期：" + str(check_time) + "秒")
                    # print(len(matches[0]), matches[0])
                    # 服务器版本检测
                    new_version = matches[0][7]
                    # 服务器版本号有变化
                    if version != new_version:
                        # 排除首次检测，服务器版本号变更，推送消息
                        if version != "":
                            chat_text = new_version
                            print(chat_text)
                            # 推送消息到synology chat
                            send_chat_message(chat_text)
                            # 推送消息到telegram
                            send_telegram_message(chat_text, 0)
                        # 新版本号赋值
                        version = new_version

                    # 服务器状态检测
                    server_new_status = matches[0][2]
                    print(server_new_status)
                    if server_status != server_new_status:
                        if server_new_status == "0":
                            chat_text = f"{server_new_status}:爆满"
                            print(chat_text)
                            # 推送消息到synology chat
                            send_chat_message(chat_text)
                            # 推送消息到telegram
                            send_telegram_message(chat_text, 0)
                        elif server_new_status == "1":
                            chat_text = f"{server_new_status}:拥挤"
                            print(chat_text)
                            # 推送消息到synology chat
                            send_chat_message(chat_text)
                            # 推送消息到telegram
                            send_telegram_message(chat_text, 0)
                        elif server_new_status == "2":
                            chat_text = f"{server_new_status}:繁忙"
                            print(chat_text)
                            # 推送消息到synology chat
                            send_chat_message(chat_text)
                            # 推送消息到telegram
                            send_telegram_message(chat_text, 0)
                        elif server_new_status == "3":
                            chat_text = f"{server_new_status}:极好"
                            print(chat_text)
                            # 推送消息到synology chat
                            send_chat_message(chat_text)
                            # 推送消息到telegram
                            send_telegram_message(chat_text, 0)
                        elif server_new_status == "4":
                            chat_text = f"{server_new_status}:维护"
                            print(chat_text)
                            # 推送消息到synology chat
                            send_chat_message(chat_text)
                            # 推送消息到telegram
                            send_telegram_message(chat_text, 0)
                        else:
                            chat_text = f"{server_new_status}:其他"
                            print(chat_text)
                            # 推送消息到synology chat
                            send_chat_message(chat_text)
                            # 推送消息到telegram
                            send_telegram_message(chat_text, 0)
                        # 判断完成后进行服务状态赋值
                        server_status = server_new_status

                    # 目标服务器ip
                    target_ip = matches[0][5]
                    # 目标服务器端口
                    target_port = int(matches[0][6])
                    # 设置最大重试次数
                    max_retries = 3
                    for retry_count in range(max_retries):
                        try:
                            # 创建一个套接字对象
                            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            # 设置连接超时时间（以秒为单位）
                            timeout = 12
                            # 设置连接超时时间
                            client_socket.settimeout(timeout)
                            # 尝试连接到目标主机
                            client_socket.connect((target_ip, target_port))
                            print(f"成功连接到 {target_ip}:{target_port}")
                            log.info(f"成功连接到 {target_ip}:{target_port}")
                            # 断开连接
                            client_socket.close()
                            # 端口开放
                            if port_status == 0:
                                port_status = 1
                                chat_text = "端口已开放"
                                # 推送消息到synology chat
                                send_chat_message(chat_text)
                                # 推送消息到telegram
                                send_telegram_message(chat_text, 0)
                                # 端口开放时，检测周期45秒一次
                                check_time = 45
                            break  # 连接成功后退出循环
                        except Exception as e:
                            print(f"连接失败: {e}")
                            if retry_count < max_retries - 1:
                                print(f"等待5秒后进行重试...")
                                time.sleep(5)
                            else:
                                print("达到最大重试次数，放弃连接尝试")
                                # 端口关闭
                                if port_status == 1:
                                    port_status = 0
                                    chat_text = "端口已关闭"
                                    # 推送消息到synology chat
                                    send_chat_message(chat_text)
                                    send_telegram_message(chat_text, 0)
                                    # 检测周期30秒
                                    check_time = 30
                else:
                    print("匹配到到数据有异常！")
                    log.info("匹配到到数据有异常！")
            else:
                print("正则匹配错误！")
                log.info("正则匹配错误！")
        else:
            print("get请求服务器失败！")
            log.info("get请求服务器失败！")

        # 每30秒检测一次
        time.sleep(check_time)


check_server_information()
