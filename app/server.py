from datetime import date, datetime, timedelta  # 导入 datetime 模块，用于处理日期和时间
import json  # 导入 json 模块，用于处理 JSON 数据
import logging  # 导入 logging 模块，用于记录日志信息
import os
import re  # 导入 re 模块，用于正则表达式匹配
import socket  # 导入 socket 模块，用于网络通信
import time  # 导入 time 模块，用于时间相关操作
import requests  # 导入 requests 模块，用于发送 HTTP 请求


# 加载配置文件
def load_config():
    try:
        with open('./config/config.json', 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        logging.error("配置文件未找到！")
    except json.JSONDecodeError as e:
        logging.error(f"配置文件解析错误: {e}")
    return {}


# 加载配置文件
config = load_config()


# 发送Telegram消息
def send_telegram_message(message, use_proxy):
    try:
        TOKEN = config["telegram"]["token"]  # 获取 Telegram 令牌
        CHAT_ID = config["telegram"]["chat_id"]  # 获取 Telegram 聊天 ID
        url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'  # 构建 Telegram 发送消息的 URL

        json_data = {
            "chat_id": CHAT_ID,  # 设置聊天 ID
            "text": message  # 设置消息文本
        }

        proxies = None
        if use_proxy:
            # 如果需要使用代理，设置代理服务器的地址
            proxies = {
                "http": "http://192.168.60.2:7890",
                "https": "http://192.168.60.2:7890"
            }

        # 发送 POST 请求到 Telegram API
        response = requests.post(url, json=json_data, proxies=proxies)

        # 检查响应状态码
        if response.status_code == 200:
            logging.info("Telegram消息发送成功。")
        else:
            logging.error("Telegram消息发送失败，状态码: %d", response.status_code)
            raise Exception("Telegram消息发送失败。")

    except Exception as e:
        logging.error("发送Telegram消息时出错: %s", str(e))
        # 在这里你可以选择是继续抛出异常，还是进行其他处理


# 发送Synology Chat消息
def send_synology_chat_message(message):
    try:
        API_URL = config["synology_chat"]["api_url"]  # 获取 Synology Chat API URL
        API_TOKEN = config["synology_chat"]["api_token"]  # 获取 Synology Chat API 令牌

        payload = {
            "api": "SYNO.Chat.External",  # 设置 API 名称
            "method": "incoming",  # 设置调用的方法
            "version": "2",  # 设置 API 版本
            "token": API_TOKEN,  # 设置 API 令牌
            "payload": json.dumps({"text": message})  # 设置消息内容
        }

        # 发送 POST 请求到 Synology Chat API
        response = requests.post(API_URL, data=payload)

        # 检查响应状态码
        if response.status_code == 200:
            logging.info("Synology Chat消息发送成功。")
        else:
            logging.error("Synology Chat消息发送失败，状态码: %d", response.status_code)
            raise Exception("Synology Chat消息发送失败。")

    except Exception as e:
        logging.error("发送Synology Chat消息时出错: %s", str(e))
        # 在这里你可以选择是继续抛出异常，还是进行其他处理


# 检查服务器信息
def check_server_information():
    # 检测周期
    check_time = 60
    # 初始化上一次检测的日期
    last_checked_date = date.today() - timedelta(days=1)
    # 获取当前脚本所在的目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    port_status = 0
    server_status = "0"
    version = ""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    url = 'http://tlbblmupdate.changyou.com/xtlbbclose-jd/loginserver.txt'  # 设置游戏服务器信息的 URL

    while True:
        # 获取当前日期
        current_date = date.today()

        # 检查日期是否变化，如果发生变化则重新配置日志和创建新的日志文件
        if current_date != last_checked_date:
            # 构建日志文件的相对路径
            log_file_name = os.path.join(script_dir, "logs/log_server", date.today().strftime('%Y%m%d.log'))
            # 创建日志文件并配置
            logging.basicConfig(filename=log_file_name, level=logging.INFO, format='%(asctime)s - %(message)s')
            last_checked_date = current_date
            logging.info("server检测程序开始执行...")
        # 发送 GET 请求获取游戏服务器信息
        response = requests.get(url=url, headers=headers)

        if response.status_code == 200:
            response.encoding = 'gb18030'
            text = response.text
            pattern = r'龙腾天下,(\d+),(\d+),(\d+),(\d+),(\d+),欢迎进入天龙内测服服务器,(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+).*?(\d+\.\d+\.\d+),'
            matches = re.findall(pattern, text)  # 使用正则表达式匹配游戏服务器信息

            if len(matches) > 0 and len(matches[0]) == 8:
                new_version = matches[0][7]
                if version != new_version and version != "":
                    chat_text = new_version
                    send_synology_chat_message(chat_text)
                    send_telegram_message(chat_text, False)
                    logging.info(chat_text)
                server_new_status = matches[0][2]
                if server_status != server_new_status:
                    status_mapping = {
                        "0": "爆满",
                        "1": "繁忙",
                        "2": "良好",
                        "3": "极佳",
                        "4": "维护",
                    }
                    chat_text = f"{server_new_status}:{status_mapping.get(server_new_status, '其他')}"
                    send_synology_chat_message(chat_text)
                    send_telegram_message(chat_text, False)
                    server_status = server_new_status
                    logging.info(chat_text)

                target_ip = matches[0][5]
                target_port = int(matches[0][6])
                # 最大重连次数
                max_retries = 3

                for retry_count in range(max_retries):
                    try:
                        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        # 超时时间
                        timeout = 12
                        client_socket.settimeout(timeout)
                        client_socket.connect((target_ip, target_port))
                        client_socket.close()

                        if port_status == 0:
                            port_status = 1
                            chat_text = "服务器已开放..."
                            send_synology_chat_message(chat_text)
                            send_telegram_message(chat_text, False)
                            check_time = 60
                            logging.info(
                                f"ip:{matches[0][5]}:{matches[0][6]} 游戏版本号：{matches[0][7]} 服务器状态：{matches[0][2]}  检测周期：{check_time}秒")
                            logging.info(f"成功连接到 {target_ip}:{target_port}")
                        break
                    except Exception as e:
                        logging.error(f"连接失败: {e}")
                        if retry_count < max_retries - 1:
                            time.sleep(5)
                        else:
                            logging.warning("达到最大重试次数，放弃连接尝试")
                            if port_status == 1:
                                port_status = 0
                                chat_text = "服务器已关闭！"
                                send_synology_chat_message(chat_text)
                                send_telegram_message(chat_text, False)
                                check_time = 30
                                logging.info(
                                    f"ip:{matches[0][5]}:{matches[0][6]} 游戏版本号：{matches[0][7]} 服务器状态：{matches[0][2]}  检测周期：{check_time}秒")
                                logging.info(chat_text)
            else:
                logging.error("匹配到的数据有异常！")
        else:
            logging.error("GET请求服务器失败！")
        time.sleep(check_time)


if __name__ == "__main__":
    try:
        check_server_information()
    except Exception as e:
        logging.error(f"发生异常: {str(e)}")
