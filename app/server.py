import json  # 导入 json 模块，用于处理 JSON 数据
import logging  # 导入 logging 模块，用于记录日志信息
import os
import re  # 导入 re 模块，用于正则表达式匹配
import socket  # 导入 socket 模块，用于网络通信
import time  # 导入 time 模块，用于时间相关操作
from datetime import date, datetime, timedelta  # 导入 datetime 模块，用于处理日期和时间

import requests  # 导入 requests 模块，用于发送 HTTP 请求


# 加载配置文件
def load_config():
    # 获取文件目录
    patch_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建文件路径
    config_dir = os.path.join(patch_dir, "config/config.json")
    try:
        with open(config_dir, 'r') as config_file:
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
        # send_telegram_message(f"发送Synology Chat消息时出错:{str(e)}", False)
        send_wechat_message(f"发送Synology Chat消息时出错:{str(e)}")
        # 在这里你可以选择是继续抛出异常，还是进行其他处理

# 发送企业微信信息
def send_wechat_message(content):
    try:
        config = load_config()
        corp_id = config["wechat"]["corp_id"]
        agent_id = config["wechat"]["agent_id"]
        secret = config["wechat"]["secret"]

        # 准备发送的消息内容
        msg = {
            "touser": "mfkd1521|vicent",  # 用户ID，可以是单个用户或多个用户，用|分隔
            "msgtype": "text",
            "agentid": agent_id,
            "text": {"content": content},
        }

        # 获取访问企业微信API的Access Token
        def get_access_token(corp_id, secret):
            url = f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corp_id}&corpsecret={secret}'
            response = requests.get(url)
            access_token = response.json().get('access_token', None)
            return access_token

        # 获取access_token
        access_token = get_access_token(corp_id, secret)

        # 如果access_token获取失败，则返回错误信息
        if not access_token:
            logging.info("wechat:获取access_token失败!")
            return "获取access_token失败"
        # 发送消息
        url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}'
        response = requests.post(url, json=msg)
        # 检查响应状态码
        if response.status_code == 200:
            logging.info("wechat消息发送成功。")
        else:
            logging.error("wechat消息发送失败，状态码: %d", response.status_code)
            raise Exception("wechat消息发送失败。")
    except Exception as e:
        logging.error("发送wechat消息时出错: %s", str(e))
        # 在这里你可以选择是继续抛出异常，还是进行其他处理

# 检查服务器信息
def check_server_information():
    # 检测周期
    check_time = 120
    # 获取当前脚本所在的目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建日志文件的相对路径
    log_file_name = os.path.join(script_dir, "logs/log_server", date.today().strftime('%Y%m%d.log'))
    # 创建日志文件并配置
    logging.basicConfig(filename=log_file_name, level=logging.INFO, format='%(asctime)s - %(message)s')
    # 记录日志的时间间隔（20分钟）
    log_interval = timedelta(minutes=20)
    # 记录日志的初始时间
    start_time = datetime.now()
    logging.info("server检测程序开始执行...")
    port_status = 1
    server_status = "0"
    version = ""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    url = 'http://tlbblmupdate.changyou.com/xtlbbclose-jd/loginserver.txt'  # 设置游戏服务器信息的 URL
    # 初次运行
    first_start = True
    status_mapping = {
        "0": "爆满",
        "1": "繁忙",
        "2": "良好",
        "3": "极佳",
        "4": "维护",
    }
    while True:
        try:
            # 发送 GET 请求获取游戏服务器信息
            response = requests.get(url=url, headers=headers)
            if response.status_code == 200:
                response.encoding = 'gb18030'
                text = response.text
                pattern = r'龙腾天下,(\d+),(\d+),(\d+),(\d+),(\d+),欢迎进入天龙内测服服务器,(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+).*?(\d+\.\d+\.\d+),'
                matches = re.findall(pattern, text)  # 使用正则表达式匹配游戏服务器信息

                if len(matches) > 0 and len(matches[0]) == 8:
                    new_version = matches[0][7]
                    server_new_status = matches[0][2]
                    target_ip = matches[0][5]
                    target_port = int(matches[0][6])
                    # 首次运行赋值
                    if first_start:
                        version = new_version
                        server_status = server_new_status
                        first_start = False
                        chat_text = (
                            f"【首次运行】：{status_mapping.get(server_new_status, '其他')}，{version}，{target_ip}:{target_port}")
                        # send_telegram_message(chat_text, False)
                        send_wechat_message(chat_text)

                    # 判断版本号
                    if version != new_version:
                        version = new_version
                        chat_text = f"需要更新：{version}"
                        # send_telegram_message(chat_text, False)
                        # send_synology_chat_message(chat_text)
                        send_wechat_message(chat_text)
                        logging.info(chat_text)
                    # 判断服务器状态
                    if server_status != server_new_status:
                        chat_text = f"{server_new_status}:{status_mapping.get(server_new_status, '其他')}"
                        # send_telegram_message(chat_text, False)
                        # send_synology_chat_message(chat_text)
                        send_wechat_message(chat_text)
                        server_status = server_new_status
                        logging.info(chat_text)
                    current_time = datetime.now()

                    # 计算距离开始运行的时间
                    elapsed_time = current_time - start_time
                    # 运行20分钟写入一次记录
                    if elapsed_time >= log_interval:
                        logging.info(
                            f"ip:{matches[0][5]}:{matches[0][6]} 游戏版本号：{matches[0][7]} 服务器状态：{matches[0][2]}  检测周期：{check_time}秒")
                        # 重置计时器
                        start_time = current_time
                    # 最大重连次数
                    max_retries = 3
                    for retry_count in range(max_retries):
                        try:
                            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            # 超时时间,正常时间10秒
                            timeout = 20
                            client_socket.settimeout(timeout)
                            client_socket.connect((target_ip, target_port))
                            client_socket.close()
                            if port_status == 0:
                                port_status = 1
                                chat_text = "服务器已开放..."
                                # send_telegram_message(chat_text, False)
                                # send_synology_chat_message(chat_text)
                                send_wechat_message(chat_text)
                                check_time = 120
                                logging.info(
                                    f"ip:{matches[0][5]}:{matches[0][6]} 游戏版本号：{matches[0][7]} 服务器状态：{matches[0][2]}  检测周期：{check_time}秒")
                                logging.info(f"成功连接到 {target_ip}:{target_port}")
                            break
                        except Exception as err:
                            logging.error(f"连接失败: {err}")
                            if retry_count < max_retries - 1:
                                time.sleep(5)
                            else:
                                logging.warning("达到最大重试次数，放弃连接尝试")
                                if port_status == 1:
                                    port_status = 0
                                    chat_text = "服务器已关闭！"
                                    # send_telegram_message(chat_text, False)
                                    # send_synology_chat_message(chat_text)
                                    send_wechat_message(chat_text)
                                    check_time = 30
                                    logging.info(
                                        f"ip:{matches[0][5]}:{matches[0][6]} 游戏版本号：{matches[0][7]} 服务器状态：{matches[0][2]}  检测周期：{check_time}秒")
                                    logging.info(chat_text)
                else:
                    logging.error("匹配到的数据有异常！")
                    # send_telegram_message("匹配到的数据有异常！", False)
                    send_wechat_message("匹配到的数据有异常！")
            else:
                logging.error("GET请求服务器失败！")
                # send_telegram_message("GET请求服务器失败！", False)
                send_wechat_message("GET请求服务器失败！")
        except requests.exceptions.RequestException as e:
            # 处理请求异常，例如网络问题
            logging.error(f"请求发生异常: {str(e)}")
            # send_telegram_message(f"请求发生异常: {str(e)}", False)
            send_wechat_message(f"请求发生异常: {str(e)}")
        except Exception as ex:
            # 处理其他异常情况
            logging.error(f"发生未知异常: {str(ex)}")
            # send_telegram_message(f"发生未知异常: {str(ex)}", False)
            send_wechat_message(f"发生未知异常: {str(ex)}")
        time.sleep(check_time)


if __name__ == "__main__":
    try:
        check_server_information()
    except Exception as e:
        logging.error(f"发生异常: {str(e)}")
