# iClicker 自动答题机器人

自动监测 iClicker Cloud 课堂投票，并自动选择指定答案（默认全选 A）。

## 功能

- 自动登录 iClicker Cloud
- 自动选择课程并等待老师开课
- 实时监测投票题目，自动选择答案
- 支持自定义答案（A/B/C/D/E）
- 支持地理位置模拟（如果课程需要签到定位）
- 多种选择器策略，兼容性强

## 安装

### 1. 确保安装了 Python 3.8+

```bash
python3 --version
```

### 2. 确保安装了 Chrome 浏览器

需要最新版本的 Google Chrome。

### 3. 安装依赖

```bash
cd /Users/xiaotianlou/Documents/iclicker
pip3 install -r requirements.txt
```

> `webdriver-manager` 会自动下载匹配你 Chrome 版本的 ChromeDriver，无需手动安装。

## 配置

编辑 `config.json` 文件，填写你的信息：

```json
{
    "email": "你的iClicker注册邮箱",
    "password": "你的iClicker密码",
    "class_name": "课程名称（部分名称即可匹配）",
    "default_answer": "A",
    "answer_delay": 3,
    "poll_interval": 5,
    "geolocation": {
        "enabled": false,
        "latitude": 0.0,
        "longitude": 0.0
    },
    "headless": false
}
```

### 配置说明

| 字段 | 说明 |
|------|------|
| `email` | iClicker 登录邮箱 |
| `password` | iClicker 登录密码 |
| `class_name` | 课程名称（支持部分匹配，比如课程全名是 "CS101 - Intro to CS"，填 "CS101" 即可） |
| `default_answer` | 默认答案，A/B/C/D/E（默认 A） |
| `answer_delay` | 检测到新题后等几秒再作答（秒），建议 2-5 秒 |
| `poll_interval` | 每隔几秒检查一次是否有新题（秒），建议 3-5 秒 |
| `geolocation.enabled` | 是否启用地理位置模拟 |
| `geolocation.latitude` | 纬度（教室位置） |
| `geolocation.longitude` | 经度（教室位置） |
| `headless` | 是否无头模式运行（不显示浏览器窗口），建议 false |

## 使用

```bash
python3 iclicker_bot.py
```

程序会：
1. 自动打开 Chrome 浏览器
2. 登录你的 iClicker 账号
3. 进入指定课程
4. 等待老师开始上课
5. 自动检测并回答所有投票题目（选 A）

按 `Ctrl+C` 可以随时停止程序。

## 注意事项

- 本程序仅支持**选择题（Multiple Choice）**类型的投票
- 建议 `headless` 设为 `false`，方便观察程序运行状态
- 如果你的课程需要地理位置验证，请开启 `geolocation` 并填入教室坐标
- 如果 iClicker 网站更新了界面，选择器可能需要更新
