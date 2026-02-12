#!/usr/bin/env python3
"""
iClicker 自动答题机器人 v2
自动登录 → 选课 → 等待开课 → 自动答 A
"""

import json
import time
import sys
import os
import signal
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    WebDriverException,
    ElementClickInterceptedException,
    InvalidSessionIdException,
)
from webdriver_manager.chrome import ChromeDriverManager

# ============================================================
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
ICLICKER_LOGIN_URL = "https://student.iclicker.com/#/login"
ICLICKER_HOME_URL = "https://student.iclicker.com/#/home"

ANSWER_MAP = {
    "A": "multiple-choice-a",
    "B": "multiple-choice-b",
    "C": "multiple-choice-c",
    "D": "multiple-choice-d",
    "E": "multiple-choice-e",
}


def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def load_config() -> dict:
    if not os.path.exists(CONFIG_FILE):
        print(f"找不到配置文件: {CONFIG_FILE}", flush=True)
        sys.exit(1)
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def is_session_dead(e: Exception) -> bool:
    """判断浏览器会话是否已断开（不可恢复）"""
    msg = str(e).lower()
    return any(kw in msg for kw in [
        "invalid session id", "session deleted", "not connected to devtools",
        "no such window", "disconnected", "target window already closed",
        "unable to connect", "connection refused",
    ])


def create_driver(config: dict) -> webdriver.Chrome:
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1200,800")
    # 保持浏览器打开（不会因为 driver 对象被回收而关闭）
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 地理位置
    geo = config.get("geolocation", {})
    if geo.get("enabled", False):
        coords = {"latitude": geo["latitude"], "longitude": geo["longitude"], "accuracy": 100}
        driver.execute_cdp_cmd("Emulation.setGeolocationOverride", coords)
        log(f"已设置地理位置: ({coords['latitude']}, {coords['longitude']})")

    return driver


def dismiss_cookie_banner(driver):
    try:
        btn = driver.find_element(By.ID, "onetrust-accept-btn-handler")
        if btn.is_displayed():
            btn.click()
            time.sleep(1)
    except Exception:
        pass


def auto_login(driver, config):
    log("正在打开 iClicker 登录页...")
    driver.get(ICLICKER_LOGIN_URL)
    time.sleep(4)
    dismiss_cookie_banner(driver)

    log("输入邮箱...")
    email_input = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "input-email"))
    )
    email_input.clear()
    email_input.send_keys(config["email"])
    time.sleep(1)

    log("输入密码...")
    pw_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "input-password"))
    )
    pw_input.clear()
    pw_input.send_keys(config["password"])
    time.sleep(1)

    log("点击登录...")
    try:
        WebDriverWait(driver, 10).until(
            lambda d: "disabled" not in d.find_element(By.ID, "sign-in-button").get_attribute("class")
        )
        driver.find_element(By.ID, "sign-in-button").click()
    except TimeoutException:
        pw_input.send_keys(Keys.ENTER)

    log("等待登录完成...")
    try:
        WebDriverWait(driver, 20).until(lambda d: "#/login" not in d.current_url)
        log("登录成功!")
    except TimeoutException:
        log(f"警告: 未检测到跳转, 当前URL: {driver.current_url}")
    time.sleep(3)


def select_course(driver, config):
    class_name = config.get("class_name", "")
    if not class_name:
        log("请在 config.json 中填写 class_name")
        sys.exit(1)

    log(f"查找课程: {class_name}")
    if "#/home" not in driver.current_url and "#/courses" not in driver.current_url:
        driver.get(ICLICKER_HOME_URL)
        time.sleep(3)

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, class_name))
    )
    time.sleep(1)
    link = driver.find_element(By.PARTIAL_LINK_TEXT, class_name)
    link.click()
    log(f"已进入课程: {class_name}")
    time.sleep(3)


def wait_and_join_class(driver):
    """等待老师开课并加入，最长等3小时"""
    log("等待老师开课中...（不要关闭 Chrome 窗口！）")
    max_wait = 10800
    start = time.time()
    consecutive_errors = 0

    while time.time() - start < max_wait:
        try:
            # 检查是否已经有选择题按钮（可能直接进入答题）
            try:
                mc = driver.find_element(By.CLASS_NAME, "multiple-choice-buttons")
                if mc.is_displayed():
                    log("检测到答题页面，直接开始!")
                    return
            except NoSuchElementException:
                pass

            # 检查 Join 按钮
            try:
                join_btn = driver.find_element(By.ID, "btnJoin")
                if join_btn.is_displayed() and join_btn.is_enabled():
                    time.sleep(1)
                    join_btn.click()
                    log("老师已开课! 已加入课堂!")
                    time.sleep(2)
                    return
            except NoSuchElementException:
                pass

            # 检查 "instructor started class" 文字
            try:
                for span in driver.find_elements(By.CLASS_NAME, "join-title"):
                    txt = span.text.strip().lower()
                    if "started class" in txt or "instructor started" in txt:
                        log("检测到老师已开课!")
                        time.sleep(2)
                        try:
                            btn = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.ID, "btnJoin"))
                            )
                            btn.click()
                            log("已加入课堂!")
                        except TimeoutException:
                            pass
                        time.sleep(2)
                        return
            except (NoSuchElementException, StaleElementReferenceException):
                pass

            consecutive_errors = 0  # 重置错误计数

            # 状态报告
            elapsed = int(time.time() - start)
            if elapsed > 0 and elapsed % 120 == 0:
                log(f"已等待 {elapsed // 60} 分钟...")

        except (InvalidSessionIdException, WebDriverException) as e:
            if is_session_dead(e):
                consecutive_errors += 1
                if consecutive_errors >= 3:
                    log("浏览器已断开连接! 请重新运行程序。")
                    raise RuntimeError("浏览器会话已断开") from e
                log(f"浏览器连接异常 ({consecutive_errors}/3)...")
            else:
                log(f"异常: {e}")
        except Exception as e:
            log(f"未知异常: {e}")

        time.sleep(5)

    raise TimeoutError("等待老师开课超时（3小时）")


def answer_polls(driver, config):
    """主循环：监测投票并自动答题"""
    choice = config.get("default_answer", "A").upper()
    delay = config.get("answer_delay", 3)
    interval = config.get("poll_interval", 5)
    answer_id = ANSWER_MAP.get(choice, ANSWER_MAP["A"])

    last_q = ""
    count = 0
    consecutive_errors = 0

    print(flush=True)
    log(f"自动答题已启动! 默认答案: {choice}")
    log(f"答题延迟: {delay}秒 | 检查间隔: {interval}秒")
    log("按 Ctrl+C 停止 | 不要关闭 Chrome 窗口!")
    print("-" * 50, flush=True)

    while True:
        try:
            current_q = _detect_question(driver)

            if current_q and current_q != last_q:
                log(f"检测到新题目!")
                if not current_q.startswith("["):
                    log(f"  内容: {current_q[:100]}")

                # 等答案按钮
                if not _wait_for_mc(driver):
                    log("不是选择题，跳过")
                    last_q = current_q
                    continue

                time.sleep(delay)

                if _click_answer(driver, answer_id, choice):
                    count += 1
                    last_q = current_q
                    log(f"已选 {choice}! (累计: {count}题)")
                else:
                    last_q = current_q
                    log("作答失败，请手动作答!")

            consecutive_errors = 0

        except (InvalidSessionIdException, WebDriverException) as e:
            if is_session_dead(e):
                consecutive_errors += 1
                if consecutive_errors >= 3:
                    log("浏览器已断开! 程序退出。")
                    break
            else:
                log(f"WebDriver异常: {e}")
        except StaleElementReferenceException:
            pass
        except Exception as e:
            log(f"异常: {e}")

        time.sleep(interval)


def _detect_question(driver) -> str:
    """检测当前是否有题目"""
    # 直接检测选择题按钮
    try:
        mc = driver.find_element(By.CLASS_NAME, "multiple-choice-buttons")
        if mc.is_displayed():
            text = _get_q_text(driver)
            return text if text else f"[poll-{int(time.time())}]"
    except (NoSuchElementException, StaleElementReferenceException):
        pass

    for cls in ["poll-question", "question-text"]:
        try:
            el = driver.find_element(By.CLASS_NAME, cls)
            if el.is_displayed() and el.text.strip():
                return el.text.strip()
        except (NoSuchElementException, StaleElementReferenceException):
            pass

    return ""


def _get_q_text(driver) -> str:
    for cls in ["question-text", "poll-question", "ng-binding"]:
        try:
            el = driver.find_element(By.CLASS_NAME, cls)
            t = el.text.strip()
            if t and len(t) > 3:
                return t
        except (NoSuchElementException, StaleElementReferenceException):
            pass
    return ""


def _wait_for_mc(driver, timeout=15) -> bool:
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "multiple-choice-buttons"))
        )
        return True
    except TimeoutException:
        return False


def _click_answer(driver, answer_id, choice) -> bool:
    # 主选择器
    try:
        btn = driver.find_element(By.ID, answer_id)
        btn.click()
        return True
    except (NoSuchElementException, ElementClickInterceptedException):
        pass

    # 备用选择器
    for sel in [f"#{answer_id}", f"[id*='choice-{choice.lower()}']",
                f".mc-button-{choice.lower()}", f"[data-answer='{choice}']"]:
        try:
            btn = driver.find_element(By.CSS_SELECTOR, sel)
            btn.click()
            return True
        except Exception:
            pass

    # 最后：点选择题区域的第一个按钮（A）
    try:
        buttons = driver.find_elements(By.CSS_SELECTOR, ".multiple-choice-buttons button")
        if buttons:
            buttons[0].click()
            return True
    except Exception:
        pass

    return False


def main():
    print(flush=True)
    print("=" * 50, flush=True)
    print("    iClicker 自动答题机器人", flush=True)
    print("=" * 50, flush=True)
    print(flush=True)

    config = load_config()
    driver = None

    def cleanup(sig=None, frame=None):
        log("正在退出...")
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    # 登录模式
    login_mode = config.get("login_mode", "auto")
    if len(sys.argv) > 1 and sys.argv[1] == "manual":
        login_mode = "manual"

    try:
        driver = create_driver(config)

        if login_mode == "manual":
            log("打开 iClicker...")
            driver.get(ICLICKER_LOGIN_URL)
            log("请在 Chrome 中手动登录，登录好后这里会自动继续...")
            # 等待用户登录完成（URL 离开 login 页面）
            WebDriverWait(driver, 300).until(lambda d: "#/login" not in d.current_url)
            log("检测到登录完成!")
            time.sleep(2)
        else:
            email = config.get("email", "")
            pw = config.get("password", "")
            if not email or email.startswith("你的") or not pw or pw.startswith("你的"):
                log("请在 config.json 中填写 email 和 password")
                sys.exit(1)
            auto_login(driver, config)

        select_course(driver, config)
        wait_and_join_class(driver)
        answer_polls(driver, config)

    except KeyboardInterrupt:
        log("用户中断")
    except RuntimeError as e:
        log(f"致命错误: {e}")
    except Exception as e:
        log(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
        log("程序已退出")


if __name__ == "__main__":
    main()
