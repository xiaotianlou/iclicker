# iClicker Auto-Answer Bot

Automatically monitors iClicker Cloud polls and selects a specified answer (default: A).

## Features

- Auto login to iClicker Cloud
- Auto select course and wait for class to start
- Real-time poll detection with auto-answer
- Customizable answer (A/B/C/D/E)
- Geolocation spoofing support
- Multiple selector strategies for compatibility
- Auto-exit on browser disconnect (no infinite loops)

## Prerequisites

- **Python 3.8+**
- **Google Chrome** (latest version)

## Installation

```bash
pip3 install -r requirements.txt
```

> `webdriver-manager` will automatically download the matching ChromeDriver version. No manual setup needed.

## Configuration

Edit `config.json` with your info:

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

### Config Options

| Field | Description |
|-------|-------------|
| `email` | iClicker login email |
| `password` | iClicker login password |
| `class_name` | Course name (partial match supported, e.g. "CS101") |
| `default_answer` | Default answer: A/B/C/D/E |
| `answer_delay` | Seconds to wait before answering (recommended: 2-5) |
| `poll_interval` | Seconds between poll checks (recommended: 3-5) |
| `login_mode` | `"auto"` or `"manual"` (login yourself in browser) |
| `geolocation.enabled` | Enable geolocation spoofing |
| `geolocation.latitude` | Classroom latitude |
| `geolocation.longitude` | Classroom longitude |

## Usage

### Auto Login (default)

```bash
python3 iclicker_bot.py
```

### Manual Login

```bash
python3 iclicker_bot.py manual
```

Or set `"login_mode": "manual"` in `config.json`.

### How It Works

1. Opens Chrome browser
2. Logs into your iClicker account
3. Enters the specified course
4. Waits for the instructor to start class
5. Auto-detects and answers all polls (selects A)

Press `Ctrl+C` to stop at any time.

## Notes

- Only supports **Multiple Choice** polls
- **Do NOT close the Chrome window** while the bot is running
- If your course requires location check-in, enable `geolocation` and enter classroom coordinates
- If iClicker updates their web interface, selectors may need updating

## Disclaimer

This tool is for educational and personal use only. Use at your own risk.
