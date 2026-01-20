# 人才引进网招聘监控

自动监控 [人才引进网](https://rcyjw.com) 的招聘信息，筛选包含特定关键词的职位，并通过邮件推送通知。

## 功能特点

- 🔍 自动抓取人才引进网最新招聘公告
- 🎯 关键词筛选：江苏、上海、浙江、安徽
- 📧 邮件推送通知
- 💬 支持微信推送（PushPlus）
- ⏰ 每日自动运行（GitHub Actions）
- 📝 自动记录历史，避免重复通知

## 快速开始

### 1. 配置 GitHub Secrets

在 GitHub 仓库的 **Settings** → **Secrets and variables** → **Actions** 中添加以下密钥：

| 密钥名称 | 说明 | 是否必需 |
|---------|------|---------|
| `SENDER_EMAIL` | 发件人邮箱（如：123456@qq.com） | ✅ 必需 |
| `EMAIL_PASS` | SMTP 授权码（不是邮箱密码！） | ✅ 必需 |
| `RECEIVER_EMAIL` | 收件人邮箱 | ✅ 必需 |
| `PUSHPLUS_TOKEN` | PushPlus Token（微信推送） | ⭕ 可选 |

### 2. 获取 QQ 邮箱 SMTP 授权码

1. 登录 QQ 邮箱网页版
2. 进入 **设置** → **账户**
3. 找到 **POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务**
4. 开启 **POP3/SMTP服务** 或 **IMAP/SMTP服务**
5. 点击 **生成授权码**，将生成的授权码填入 `EMAIL_PASS`

### 3. 手动触发运行

进入仓库的 **Actions** 标签页，选择 **每日人才引进招聘监控**，点击 **Run workflow** 手动触发。

## 配置说明

### 修改关键词

编辑 `config.py` 文件中的 `KEYWORDS` 列表：

```python
KEYWORDS = ['江苏', '上海', '浙江', '安徽']
```

### 修改抓取天数

编辑 `config.py` 文件中的 `LOOKBACK_DAYS`：

```python
LOOKBACK_DAYS = 3  # 抓取最近 3 天的数据
```

### 修改运行时间

编辑 `.github/workflows/daily_run.yml` 文件中的 cron 表达式：

```yaml
schedule:
  - cron: '0 1 * * *'  # 每天北京时间 9:00 (UTC 1:00)
```

## 本地运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置邮箱信息（在 config.py 中直接填写或使用环境变量）
# 编辑 config.py，填写 SENDER_EMAIL、EMAIL_PASS、RECEIVER_EMAIL

# 3. 运行脚本
python main.py
```

## 项目结构

```
TalentIntro_Monitor/
├── .github/
│   └── workflows/
│       └── daily_run.yml    # GitHub Actions 工作流
├── config.py                # 配置文件
├── main.py                  # 主程序
├── requirements.txt         # 依赖列表
├── history.txt             # 历史记录（自动生成）
└── README.md               # 说明文档
```

## 通知示例

当发现符合条件的招聘信息时，会收到如下邮件：

```
【人才引进网】发现 2 条新招聘 (2026-01-20)

日期: 2026-01-20
关键词: ['江苏', '上海', '浙江', '安徽']

发现以下 2 条相关招聘:
- [2026-01-20] 南京市气象部门2026年招聘2名高层次人才公告
  链接: https://rcyjw.com/jiangsu/nanjing/129113.html
- [2026-01-20] 2026年合肥市万泉河路幼儿园、合肥市杭州路幼儿园招聘启事
  链接: https://rcyjw.com/anhui/hefei/129211.html
```

## 常见问题

### Q: 为什么没有收到邮件？

1. 检查 GitHub Secrets 是否配置正确
2. 确认使用的是 SMTP 授权码，而不是邮箱登录密码
3. 查看 Actions 运行日志，确认是否有错误信息

### Q: 如何避免重复通知？

程序会自动生成 `history.txt` 文件记录已处理的招聘信息，避免重复通知。

### Q: 可以监控其他关键词吗？

可以！修改 `config.py` 中的 `KEYWORDS` 列表即可。

## 许可证

MIT License

## 致谢

本项目参考了 [NJHRSS_Monitor](https://github.com/Simple53/NJHRSS_Monitor) 项目。