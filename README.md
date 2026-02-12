# iClicker Auto-Answer Bot / iClicker 自动答题机器人

Automatically monitors iClicker Cloud polls and selects a specified answer (default: A).

自动监测 iClicker Cloud 课堂投票，并自动选择指定答案（默认全选 A）。

## Features / 功能

- Auto login to iClicker Cloud / 自动登录 iClicker Cloud
- Auto select course and wait for class to start / 自动选课并等待老师开课
- Real-time poll detection with auto-answer / 实时监测投票，自动作答
- Customizable answer (A/B/C/D/E) / 支持自定义答案
- Geolocation spoofing support / 支持地理位置模拟
- Multiple selector strategies for compatibility / 多种选择器策略，兼容性强
- Auto-exit on browser disconnect (no infinite loops) / 浏览器断开时自动退出

## Prerequisites / 前置要求

- **Python 3.8+**
- **Google Chrome** (latest version / 最新版本)

## Installation / 安装

```bash
pip3 install -r requirements.txt
```

> `webdriver-manager` will automatically download the matching ChromeDriver version.
>
> `webdriver-manager` 会自动下载匹配你 Chrome 版本的 ChromeDriver，无需手动安装。

## Configuration / 配置

Edit `config.json` with your info / 编辑 `config.json`，填写你的信息：

```json
{
    "email": "your-iclicker-email@example.com",
    "password": "your-password",
    "class_name": "COURSE_NAME",
    "default_answer": "A",
    "answer_delay": 3,
    "poll_interval": 5,
    "login_mode": "auto",
    "geolocation": {
        "enabled": false,
        "latitude": 0.0,
        "longitude": 0.0
    }
}
```

### Config Options / 配置说明

| Field | Description | 说明 |
|-------|-------------|------|
| `email` | iClicker login email | 登录邮箱 |
| `password` | iClicker login password | 登录密码 |
| `class_name` | Course name (partial match supported, e.g. "CS101") | 课程名称（支持部分匹配） |
| `default_answer` | Default answer: A/B/C/D/E | 默认答案 |
| `answer_delay` | Seconds to wait before answering (recommended: 2-5) | 检测到新题后等几秒再答 |
| `poll_interval` | Seconds between poll checks (recommended: 3-5) | 每隔几秒检查新题 |
| `login_mode` | `"auto"` or `"manual"` (login yourself in browser) | 登录模式：自动或手动 |
| `geolocation.enabled` | Enable geolocation spoofing | 是否启用位置模拟 |
| `geolocation.latitude` | Classroom latitude | 教室纬度 |
| `geolocation.longitude` | Classroom longitude | 教室经度 |

## Usage / 使用

### Auto Login / 自动登录

```bash
python3 iclicker_bot.py
```

### Manual Login / 手动登录

```bash
python3 iclicker_bot.py manual
```

Or set `"login_mode": "manual"` in `config.json`.

### What it does / 运行流程

1. Opens Chrome browser / 打开 Chrome 浏览器
2. Logs into your iClicker account / 登录 iClicker 账号
3. Enters the specified course / 进入指定课程
4. Waits for the instructor to start class / 等待老师开课
5. Auto-detects and answers all polls (selects A) / 自动检测并回答所有投票题

Press `Ctrl+C` to stop at any time. / 按 `Ctrl+C` 随时停止。

## Notes / 注意事项

- Only supports **Multiple Choice** polls / 仅支持选择题
- **Do NOT close the Chrome window** while running / 运行时不要关闭 Chrome 窗口
- If your course requires location check-in, enable `geolocation` and enter classroom coordinates / 如需位置验证，开启 `geolocation` 并填入教室坐标
- If iClicker updates their web interface, selectors may need updating / 如 iClicker 更新界面，选择器可能需要更新

## Disclaimer / 免责声明

This tool is for educational and personal use only. Use at your own risk.

本工具仅供学习和个人使用，风险自负。
