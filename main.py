import requests
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime, timedelta
import time
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from urllib.parse import urljoin

import config

def get_session():
    s = requests.Session()
    s.headers.update(config.HEADERS)
    return s

def clean_filename(name):
    name = re.sub(r'[\\/*?:"<>|\r\n]', "_", name)
    name = re.sub(r'\s+', " ", name)
    return name.strip()[:100]

def send_wechat(msg_title, msg_content):
    if not config.PUSHPLUS_TOKEN: return
    url = 'http://www.pushplus.plus/send'
    data = {"token": config.PUSHPLUS_TOKEN, "title": msg_title, "content": msg_content, "template": "html"}
    try:
        requests.post(url, json=data, timeout=10)
        print(">>> 微信推送请求已发送")
    except Exception as e:
        print(f"微信推送失败: {e}")

def notify_user(new_items):
    today_str = datetime.now().strftime("%Y-%m-%d")
    count = len(new_items)
    
    if count == 0:
        print(">>> 无新增内容，跳过通知。")
        return

    title = f"【人才引进网】发现 {count} 条新招聘 ({today_str})"
    
    content = f"日期: {today_str}\n"
    content += f"关键词: {config.KEYWORDS}\n"
    content += f"排除关键词: {config.EXCLUDE_KEYWORDS}\n\n"
    content += f"发现以下 {count} 条相关招聘:\n"
    
    html_list = ""
    for item in new_items:
        content += f"- [{item['date']}] {item['title']}\n  链接: {item['link']}\n"
        html_list += f"<li><span style='color:#666'>[{item['date']}]</span> <a href='{item['link']}'>{item['title']}</a></li>"
    
    print(f">>> 准备发送通知: {title}")
    
    # 微信推送
    if config.PUSHPLUS_TOKEN:
        wechat_content = content.replace("\n", "<br>")
        send_wechat(title, wechat_content)
    
    # 邮件推送
    if config.EMAIL_ENABLE:
        html_content = f"""
        <h3>{title}</h3>
        <p>日期: {today_str}</p>
        <p>关键词: {config.KEYWORDS}</p>
        <p>排除关键词: {config.EXCLUDE_KEYWORDS}</p>
        <hr>
        <ul>
            {html_list}
        </ul>
        <hr>
        <p><a href="{config.BASE_URL}">前往人才引进网</a></p>
        """
        
        msg = MIMEText(html_content, 'html', 'utf-8')
        msg['Subject'] = Header(title, 'utf-8')
        msg['From'] = formataddr(["人才引进网助手", config.SENDER_EMAIL])
        msg['To'] = formataddr(["用户", config.RECEIVER_EMAIL])

        try:
            server = smtplib.SMTP_SSL(config.SMTP_SERVER, config.SMTP_PORT)
            server.login(config.SENDER_EMAIL, config.EMAIL_PASS)
            server.sendmail(config.SENDER_EMAIL, [config.RECEIVER_EMAIL], msg.as_string())
            server.quit()
            print(">>> 邮件发送成功")
        except Exception as e:
            print(f"邮件发送失败: {e}")

def run_scraper():
    print("=" * 40)
    print(">>> 开始执行爬虫任务")
    print("=" * 40)
    
    lookback_days = config.LOOKBACK_DAYS
    end_date_obj = datetime.now().date()
    start_date_obj = end_date_obj - timedelta(days=lookback_days - 1)
    print(f">>> 抓取范围: {start_date_obj} 至 {end_date_obj}")

    session = get_session()
    
    # 用来记录已经处理过的链接，防止重复（这里简单用文件记录，或者仅本次运行内存去重）
    # 简单的实现：每次都抓，但只通知今天发布或最近几天发布的
    # 为了避免重复通知，最好有一个历史记录文件。
    # 这里我们采用 simpler approach: 只通知在 LOOKBACK_DAYS 内的，且假设用户每天运行。
    # 如果要避免重复通知，可以增加 history.txt
    
    history_file = os.path.join(os.path.dirname(__file__), "history.txt")
    history_set = set()
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            for line in f:
                history_set.add(line.strip())

    found_items = []
    
    # 翻页逻辑
    current_url = config.BASE_URL
    page_num = 1
    stop_flag = False
    
    while not stop_flag:
        print(f"\n--- 第 {page_num} 页 ---\n    URL: {current_url}")
        
        try:
            res = session.get(current_url, timeout=15)
            if res.status_code == 404:
                break
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 列表选择器: ul.lie1 > li
            ul = soup.find('ul', class_='lie1')
            if not ul:
                print("    未找到列表元素 ul.lie1")
                break
                
            lis = ul.find_all('li')
            if not lis:
                print("    本页无内容")
                if page_num > 1: break
            
            for li in lis:
                # 结构: <em>2026-01-20</em><a href="...">Title</a>
                em = li.find('em')
                a_tag = li.find('a')
                
                if not em or not a_tag: continue
                
                date_str = em.get_text(strip=True)
                title = a_tag.get_text(strip=True)
                link = a_tag.get('href')
                # 将相对链接转换为完整URL
                if link and not link.startswith('http'):
                    link = urljoin(current_url, link)
                
                try:
                    item_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError: continue
                
                if item_date < start_date_obj:
                    stop_flag = True # 超出时间范围，停止
                    break
                
                # 关键词过滤
                if any(kw in title for kw in config.KEYWORDS):
                    # 排除关键词过滤
                    if any(exclude_kw in title for exclude_kw in config.EXCLUDE_KEYWORDS):
                        print(f"  [排除] 包含排除关键词: {title}")
                        continue
                    
                    # 检查是否历史已记录
                    unique_id = f"{date_str}_{title}"
                    if unique_id in history_set:
                        print(f"  [跳过] 已记录: {title}")
                        continue
                        
                    print(f"  > 发现: [{date_str}] {title}")
                    found_items.append({
                        "date": date_str,
                        "title": title,
                        "link": link
                    })
                    history_set.add(unique_id)
            
            if stop_flag: break
            
            # 构造下一页 URL
            # 首页: type_0.html
            # 第2页: type_0_1.html ? No, usually type_0_1.html is page 2.
            # Let's check the pagination links in the HTML content provided previously.
            # <a href="https://rcyjw.com/type_0_1.html">2</a>
            # So page 2 is type_0_1.html.
            # Page n is type_0_{n-1}.html
            
            page_num += 1
            next_url = f"https://rcyjw.com/type_0_{page_num-1}.html"
            current_url = next_url
            time.sleep(1)
            
        except Exception as e:
            print(f"    [错误] 页面抓取失败: {e}")
            break
            
    # 保存历史记录
    with open(history_file, 'w', encoding='utf-8') as f:
        for uid in history_set:
            f.write(uid + "\n")
            
    return found_items

if __name__ == "__main__":
    new_items = run_scraper()
    notify_user(new_items)
