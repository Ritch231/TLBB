import json  # 导入 json 模块，用于处理 JSON 数据
import logging  # 导入 logging 模块，用于记录日志信息
import os
import re
import time
from datetime import date, datetime, timedelta

import requests
from lxml import html


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


# 发送Telegram消息
def send_telegram_message(message, use_proxy):
    try:
        # 加载配置文件
        config = load_config()
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
        # 加载配置文件
        config = load_config()
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


# 将内容写入文件
def append_to_file(filename, content):
    with open(filename, 'a') as file:
        file.write(content)


# 在文件内搜索内容是否存在
def search_multiline_text(filename, search_text):
    # 文件不存在则先创建文件
    if not os.path.isfile(filename):
        with open(filename, 'w') as file:
            file.write('')
        logging.info(f'创建文件 {filename}')

    with open(filename, 'r') as file:
        lines = file.readlines()

    search_lines = search_text.splitlines()
    num_lines = len(search_lines)
    num_file_lines = len(lines)

    for i in range(num_file_lines - num_lines + 1):
        if all(lines[i + j].strip() == search_lines[j].strip() for j in range(num_lines)):
            return True

    return False


# 发送请求等url
url = 'http://bbs.tl.changyou.com/forum.php?mod=forumdisplay&fid=504'
# 添加协议头，否则网站请求403
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
}


def check():
    # 获取当前脚本所在的目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建日志文件的相对路径
    log_file_name = os.path.join(script_dir, "logs/log_bbs", date.today().strftime('%Y%m%d.log'))
    # 创建日志文件并配置
    logging.basicConfig(filename=log_file_name, level=logging.INFO, format='%(asctime)s - %(message)s')
    logging.info("bbs检测程序开始执行...")
    # 记录更新内容的文件
    bbs_filename = os.path.join(script_dir, "logs/log_bbs", "tlbbs.txt")
    while True:
        # 今天是否有更新
        is_get_message = False
        try:
            # 发送GET请求
            response = requests.get(url, headers=headers)
            # 检查响应状态码
            if response.status_code == 200:
                # 请求成功，继续处理响应内容
                # 使用response.content来获取HTML内容，而不是response.text
                html_content = response.content
                # 解析HTML内容
                root = html.fromstring(html_content)
                try:
                    # 使用XPath选择整个表格
                    table = root.xpath('//table[@id="threadlisttableid"]')[0]
                    # 遍历表格的每一行
                    for row in table.xpath('.//tr'):
                        # 遍历每一行的单元格并提取文本内容
                        cells = row.xpath('.//td|th')
                        row_data = [cell.text_content().strip() for cell in cells]
                        # print(f"行数据: {row_data}")
                        # 获取更新公告的标题
                        table_title = row_data[1]
                        # 标题替换不需要的内容
                        table_title = table_title.replace("预览\r\n ", "").replace("\r\n\r\nNew", "")
                        # 判断标题是否含有内测关键词
                        # if "龙腾天下" in table_title or "龙啸苍穹" in table_title or "内测" in table_title or "龙门" in table_title:
                        if any(keyword in table_title for keyword in ["龙腾天下", "龙啸苍穹", "内测", "龙门"]):
                            # 获取公告发布时间，如：“admin002 \r\n2023-8-11 17:28”
                            input_string = row_data[2]
                            # 正则匹配出公告时间，如：“2023-8-15”
                            pattern = r'(\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2})'
                            # 使用re.findall()进行匹配
                            matches = re.findall(pattern, input_string)
                            # 如果有匹配项，提取第一个匹配项
                            if matches:
                                date_time = matches[0]
                                # 解析时间字符串，转换为datetime对象 "2023-8-7 11:24" 转为 “2023-08-07 11:24:00”
                                time_obj = datetime.strptime(date_time, '%Y-%m-%d %H:%M')
                                # print(date_time, time_obj)
                                # 获取当前时间，提取年月日
                                now = datetime.now()
                                now_year, now_month, now_day = now.year, now.month, now.day
                                # 根据解析时间的年月日，判断是否是今天的最新公告
                                if time_obj.year == now_year and time_obj.month == now_month and time_obj.day == now_day:
                                    # 发现更新
                                    is_get_message = True
                                    # if time_obj.year == 2023 and time_obj.month == 9 and time_obj.day == 7:
                                    # 使用XPath来获取链接
                                    link_elements = row.xpath('.//td[@class="num"]/a[@class="xi2"]/@href')
                                    # 检查是否找到链接元素
                                    if link_elements:
                                        # 获取到对应连接
                                        link = "http://bbs.tl.changyou.com/" + link_elements[0]
                                        response = requests.get(link, headers=headers)
                                        # 解析HTML内容
                                        tree = html.fromstring(response.content)
                                        # 定义XPath表达式来选择所需的文本
                                        xpath_expression = "//td[@class='t_f']/text()"
                                        # 使用XPath提取文本
                                        text = tree.xpath(xpath_expression)
                                        # 将提取的文本连接成一个单独的字符串
                                        result = "".join(text).strip()
                                        # 推送消息：标题+更新内容
                                        send_message = table_title + '\r\n' + result + '\r\n'
                                        is_have = search_multiline_text(bbs_filename, send_message)
                                        if is_have:
                                            logging.info("已推送更新内容")
                                        else:
                                            append_to_file(bbs_filename, send_message)
                                            # send_telegram_message(send_message, False)
                                            # send_synology_chat_message(send_message)
                                            send_wechat_message(send_message)
                                            logging.info("记录并推送消息...")
                                            logging.info(f"行数据: {row_data}")
                                            logging.info(f"链接: {link}")
                                    else:
                                        logging.warning(f"行数据: {row_data}")
                                        logging.warning("链接: 无")
                            else:
                                logging.warning("未找到匹配的日期时间信息")
                    if not is_get_message:
                        logging.info("今天没有更新！")
                except IndexError:
                    logging.error("无法找到指定表格。可能是网页结构变化或XPath表达式错误。")
                    # 在这里你可以添加适当的处理代码，例如终止脚本或进行其他操作。
            else:
                logging.error("GET请求失败，状态码: %d", response.status_code)
                # 在这里你可以选择终止脚本、记录错误信息或采取其他操作
        except requests.exceptions.RequestException as e:
            logging.error("发送GET请求时出错：%s", str(e))
            # 在这里你可以处理网络请求异常，例如终止脚本、记录错误信息或采取其他操作
            # send_telegram_message(f"发送GET请求时出错：{str(e)}", False)
            send_wechat_message(f"发送GET请求时出错：{str(e)}")
        time.sleep(180)


check()
