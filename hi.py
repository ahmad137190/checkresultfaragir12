from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from PIL import Image, ImageOps, ImageFilter
import requests
import time
import platform
import subprocess
import os
import re
import pytesseract

# ---------------- OCR-based CAPTCHA Solver ----------------
def normalize(text: str) -> str:
    text = text.replace('x', '*').replace('X', '*').replace('×', '*')
    text = re.sub(r'[=≥<>].*$', '', text)
    return text.strip()

def is_safe_expression(expr: str) -> bool:
    return re.fullmatch(r'\d+[\+\-\*/]\d+', expr) is not None

def solve_captcha(image_filename):
    if not os.path.isfile(image_filename):
        return f"فایل '{image_filename}' پیدا نشد."

    img = Image.open(image_filename)
    gray = img.convert('L')
    contrast = ImageOps.autocontrast(gray)
    binary = contrast.point(lambda x: 0 if x < 140 else 255, '1')
    clean_img = binary.filter(ImageFilter.MedianFilter(3))

    raw_text = pytesseract.image_to_string(clean_img, config='--psm 7')
    text = normalize(raw_text)

    print("clean:", text)  # دیباگ

    if not is_safe_expression(text):
        return "خطا در تشخیص کپچا"

    try:
        return str(eval(text))
    except Exception as e:
        return f"خطا در محاسبه: {e}"

# ---------------- Driver Setup ----------------
def create_driver():
    options = Options()
    options.headless = True  # برای نمایش مرورگر: False
    chromedriver_path = r"D:\chromedriver.exe" if platform.system() == "Windows" else "/usr/local/bin/chromedriver"
    service = Service(chromedriver_path)
    return webdriver.Chrome(service=service, options=options)

# ---------------- Login and Cookie ----------------
def login_and_get_cookies():
    global cookie_string
    driver = create_driver()
    try:
        driver.get("https://az12.hrtc.ir/hrt/profile/")
        wait = WebDriverWait(driver, 10)

        csrf_token = wait.until(EC.presence_of_element_located((By.NAME, 'csrfmiddlewaretoken'))).get_attribute('value')
        print("CSRF Token:", csrf_token)

        driver.find_element(By.ID, 'id_national_code').send_keys('0520525264')
        driver.find_element(By.ID, 'id_track_code').send_keys('8777426094')

        captcha_img = driver.find_element(By.CSS_SELECTOR, 'img.captcha')
        captcha_path = "captcha.png"
        captcha_img.screenshot(captcha_path)
        print(f"✅ تصویر کپچا ذخیره شد: {captcha_path}")

        captcha_text = solve_captcha(captcha_path)
        if "خطا" in captcha_text:
            captcha_text = input("🔤 کد کپچا را به‌صورت دستی وارد کنید: ")

        driver.find_element(By.ID, 'id_captcha_1').send_keys(captcha_text)
        driver.find_element(By.ID, 'submit-id-submit').click()

        time.sleep(5)
        selenium_cookies = driver.get_cookies()
        expiry_time = datetime.utcnow() + timedelta(hours=24)

        cookies_with_expiry = []
        for cookie in selenium_cookies:
            cookie_str = f"{cookie['name']}={cookie['value']}; Expires={expiry_time.strftime('%a, %d %b %Y %H:%M:%S GMT')}"
            cookies_with_expiry.append(cookie_str)

        cookie_string = "; ".join(cookies_with_expiry)
        print("🍪 کوکی‌ها:", cookie_string)
    finally:
        driver.quit()

# ---------------- Send SMS ----------------
def send_sms():
    sms_url = "https://api.sms.ir/v1/send/bulk"
    payload = {
        "lineNumber": 30007732003728,
        "messageText": "📢 جواب نهایی اومد",
        "mobiles": [
            "+989189561009", "+989383734216", "+989108663748",
            "+989940715285", "+989188872523", "+989389354268", "+989999371232"
        ]
    }
    headers_sms = {
        'X-API-KEY': 'CYSZ6awyphlQemyp7zztiqwnIxr3qzi54UC1VMcenxdc1U40',
        'Content-Type': 'application/json'
    }
    try:
        r = requests.post(sms_url, json=payload, headers=headers_sms)
        print(f"📩 پیامک ارسال شد: {r.text} - {datetime.now()}")
    except Exception as e:
        print(f"⚠️ خطا در ارسال پیامک: {e} - {datetime.now()}")

def display_image_in_terminal(image_path="success.png"):
    try:
        img = Image.open(image_path).resize((50, 25)).convert("L")
        chars = "@%#*+=-:. "
        ascii_str = "".join(chars[pixel // 25] for pixel in img.getdata())
        ascii_str = "\n".join([ascii_str[i:(i + 50)] for i in range(0, len(ascii_str), 50)])
        print(ascii_str)
    except Exception as e:
        print(f"⚠️ خطا در نمایش تصویر: {e}")

# ---------------- Main Loop ----------------
login_and_get_cookies()
cookies = {item.split("=")[0].strip(): item.split("=")[1].strip().split(";")[0] for item in cookie_string.split(";")}

url = "https://az12.hrtc.ir/hrt/pl/home/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

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
                    print(f"✅ اعلام نتیجه نهایی فعال شد! - {datetime.now()}")
                    send_sms()
                    display_image_in_terminal()

                    if platform.system() == "Windows":
                        subprocess.run(["start", "mplay32"], shell=True)
                    elif platform.system() == "Darwin":
                        subprocess.run(["afplay", "/System/Library/Sounds/Ping.aiff"])
                    break
                else:
                    print(f"⏳ هنوز فعال نیست... - {datetime.now()}")
                    was_disabled = is_disabled
            else:
                print("⚠️ لینک مرتبط پیدا نشد.")
        else:
            not_found_count += 1
            print(f"❌ متن یافت نشد - {datetime.now()}")
            if not_found_count >= 10:
                print("🔁 تلاش برای ورود مجدد...")
                login_and_get_cookies()
                cookies = {item.split("=")[0].strip(): item.split("=")[1].strip().split(";")[0] for item in cookie_string.split(";")}
                not_found_count = 0
    except Exception as e:
        print(f"⚠️ خطا: {e} - {datetime.now()}")
    time.sleep(30)
