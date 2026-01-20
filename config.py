import os

# ================= 爬虫筛选关键词 =================
# 包含以下任一关键词的标题才会被保留
KEYWORDS = ['江苏', '上海', '浙江', '安徽']

# ================= 基础配置 =================
# 目标网址 (人才引进网 - 事业单位招聘)
BASE_URL = "https://rcyjw.com/type_0.html"

# 文件/数据保存目录
SAVE_DIR = "招聘公告"

# 抓取时间范围设置 (往前回溯天数)
LOOKBACK_DAYS = 3 

# GitHub 仓库链接（用于邮件通知，可选）
REPO_URL = ""

# 请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

# ================= 通知与账号配置 =================
# 优先使用环境变量
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN", "")

# 邮箱推送配置
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "")      # 发件人邮箱
EMAIL_PASS = os.environ.get("EMAIL_PASS", "")          # SMTP授权码
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL", "")  # 收件人邮箱

# 邮件服务器配置 (默认QQ邮箱)
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465

# 自动判断是否开启邮件
EMAIL_ENABLE = True if (EMAIL_PASS and SENDER_EMAIL and RECEIVER_EMAIL) else False
