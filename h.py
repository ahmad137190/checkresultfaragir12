from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests
from bs4 import BeautifulSoup
import time
from PIL import Image
from datetime import datetime, timedelta
import os
import subprocess
import platform

# ---------- تنظیمات 2Captcha ----------
API_KEY_2CAPTCHA = '4492be086313f81c3baaf4738f2c9c61'

def solve_captcha_2captcha(image_path):
    print("در حال ارسال کپچا به 2Captcha...")
    with open(image_path, 'rb') as f:
        captcha_data = f.read()
    response = requests.post("http://2captcha.com/in.php",
                             files={'file': captcha_data},
                             data={'key': API_KEY_2CAPTCHA, 'method': 'post'})
    if response.status_code != 200 or 'OK|' not in response.text:
        print("❌ خطا در ارسال کپچا:", response.text)
        return None

    captcha_id = response.text.split('|')[1]
    print(f"✅ کپچا ارسال شد (ID: {captcha_id})")

    for i in range(24):
        time.sleep(7)
        result = requests.get(f"http://2captcha.com/res.php?key={API_KEY_2CAPTCHA}&action=get&id={captcha_id}")
        if result.status_code == 200:
            if 'OK|' in result.text:
                return result.text.split('|')[1]
            elif 'CAPCHA_NOT_READY' in result.text:
                print("⏳ کپچا هنوز آماده نیست...")
                continue
            else:
                print("❌ خطا در پاسخ کپچا:", result.text)
                return None
    print("⏰ زمان پاسخ کپچا به پایان رسید.")
    return None

# ---------- ایجاد درایور ----------
def create_driver():
    options = Options()
    options.headless = True  # اگر می‌خوای مرورگر رو ببینی، False کن

    # مسیر chromedriver بر اساس سیستم‌عامل
    if platform.system() == "Windows":
        chromedriver_path = r"D:\chromedriver.exe"
    else:
        chromedriver_path = "/usr/local/bin/chromedriver"

    service = Service(chromedriver_path)
    return webdriver.Chrome(service=service, options=options)

# ---------- ورود و گرفتن کوکی با expire 24 ساعت ----------
def login_and_get_cookies():
    global cookie_string
    driver = create_driver()
    try:
        driver.get("https://az12.hrtc.ir/hrt/profile/")
        wait = WebDriverWait(driver, 10)

        csrf_token_input = wait.until(EC.presence_of_element_located((By.NAME, 'csrfmiddlewaretoken')))
        csrf_token = csrf_token_input.get_attribute('value')
        print("CSRF Token:", csrf_token)

        driver.find_element(By.ID, 'id_national_code').send_keys('0520525264')
        driver.find_element(By.ID, 'id_track_code').send_keys('8777426094')

        captcha_img = driver.find_element(By.CSS_SELECTOR, 'img.captcha')
        captcha_path = "captcha.png"
        captcha_img.screenshot(captcha_path)
        print(f"✅ تصویر کپچا ذخیره شد: {captcha_path}")

        captcha_text = solve_captcha_2captcha(captcha_path)
        if not captcha_text:
            captcha_text = input("🔤 کد کپچا را وارد کنید: ")

        driver.find_element(By.ID, 'id_captcha_1').send_keys(captcha_text)
        driver.find_element(By.ID, 'submit-id-submit').click()

        time.sleep(5)
        selenium_cookies = driver.get_cookies()

        # تنظیم expire 24 ساعته
        expiry_time = datetime.utcnow() + timedelta(hours=24)
        cookies_with_expiry = []
        for cookie in selenium_cookies:
            cookie_str = f"{cookie['name']}={cookie['value']}"
            cookie_str += f"; Expires={expiry_time.strftime('%a, %d %b %Y %H:%M:%S GMT')}"
            cookies_with_expiry.append(cookie_str)

        cookie_string = "; ".join(cookies_with_expiry)
        print("🍪 کوکی‌ها با تاریخ انقضا:", cookie_string)
    finally:
        driver.quit()

# ---------- شروع ورود ----------
login_and_get_cookies()

cookies = {item.split("=")[0].strip(): item.split("=")[1].strip().split(";")[0] for item in cookie_string.split(";")}
# توجه: وقتی expire اضافه می‌کنیم، باید فقط نام و مقدار رو بگیریم برای کوکی در requests

url = "https://az12.hrtc.ir/hrt/pl/home/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def get_current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def send_sms():
    sms_url = "https://api.sms.ir/v1/send/bulk"
    payload = {
        "lineNumber": 30007732003728,
        "messageText": "📢 جواب نهایی اومد",
        "mobiles": [
            "+989189561009",
            "+989383734216",
            "+989108663748",
            "+989940715285",
            "+989188872523",
            "+989389354268",
            "+989999371232"
        ]
    }
    headers_sms = {
        'X-API-KEY': 'CYSZ6awyphlQemyp7zztiqwnIxr3qzi54UC1VMcenxdc1U40',
        'Content-Type': 'application/json'
    }
    try:
        r = requests.post(sms_url, json=payload, headers=headers_sms)
        print(f"📩 پیامک ارسال شد: {r.text} - {get_current_timestamp()}")
    except Exception as e:
        print(f"⚠️ خطا در ارسال پیامک: {e} - {get_current_timestamp()}")

def display_image_in_terminal(image_path="success.png"):
    try:
        img = Image.open(image_path).resize((50, 25)).convert("L")
        chars = "@%#*+=-:. "
        ascii_str = "".join(chars[pixel // 25] for pixel in img.getdata())
        ascii_str = "\n".join([ascii_str[i:(i + 50)] for i in range(0, len(ascii_str), 50)])
        print(ascii_str)
    except Exception as e:
        print(f"⚠️ خطا در نمایش تصویر: {e}")

# ---------- حلقه بررسی وضعیت ----------
was_disabled = True
not_found_count = 0

while True:
    try:
        response = requests.get(url, headers=headers, cookies=cookies)
        soup = BeautifulSoup(response.text, "html.parser")
        target_p = soup.find("p", string="اعلام نتیجه نهایی")
        if target_p:
            not_found_count = 0
            parent_a = target_p.find_parent("a")
            if parent_a:
                is_disabled = 'disabled' in parent_a.get("class", [])
                if was_disabled and not is_disabled:
                    print(f"✅ اعلام نتیجه نهایی فعال شد! - {get_current_timestamp()}")
                    send_sms()
                    display_image_in_terminal()

                    # اجرای پلیر صوتی بر اساس سیستم‌عامل
                    if platform.system() == "Windows":
                        subprocess.run(["start", "mplay32"], shell=True)
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.run(["afplay", "/System/Library/Sounds/Ping.aiff"])
                    else:
                        print("🔊 صدای اعلام نتیجه فعال نشده (سیستم‌عامل ناشناخته)")

                    break
                else:
                    print(f"⏳ هنوز فعال نیست... - {get_current_timestamp()}")
                    was_disabled = is_disabled
            else:
                print("⚠️ لینک مرتبط پیدا نشد.")
        else:
            not_found_count += 1
            print(f"❌ متن مورد نظر پیدا نشد - {get_current_timestamp()}")
            if not_found_count >= 10:
                print("🔁 ورود مجدد...")
                login_and_get_cookies()
                cookies = {item.split("=")[0].strip(): item.split("=")[1].strip().split(";")[0] for item in cookie_string.split(";")}
                not_found_count = 0
    except Exception as e:
        print(f"⚠️ خطا: {e} - {get_current_timestamp()}")
    time.sleep(30)
