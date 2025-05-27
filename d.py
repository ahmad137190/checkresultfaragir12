from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests
from bs4 import BeautifulSoup
import time
import subprocess
from PIL import Image
from datetime import datetime, timedelta
import os

# ----------- تنظیمات 2Captcha -----------
API_KEY_2CAPTCHA = '4492be086313f81c3baaf4738f2c9c61'  # اینجا کلید 2captcha خودتون رو بگذارید

def solve_captcha_2captcha(image_path):
    print("ارسال کپچا به 2Captcha برای حل شدن...")
    with open(image_path, 'rb') as f:
        captcha_data = f.read()
    response = requests.post("http://2captcha.com/in.php",
                             files={'file': captcha_data},
                             data={'key': API_KEY_2CAPTCHA, 'method': 'post'})
    if response.status_code != 200 or 'OK|' not in response.text:
        print("خطا در ارسال کپچا به 2Captcha:", response.text)
        return None

    captcha_id = response.text.split('|')[1]
    print(f"کپچا ارسال شد، شناسه: {captcha_id}")

    for i in range(24):
        time.sleep(7)
        result_response = requests.get(f"http://2captcha.com/res.php?key={API_KEY_2CAPTCHA}&action=get&id={captcha_id}")
        if result_response.status_code == 200:
            if 'OK|' in result_response.text:
                captcha_text = result_response.text.split('|')[1]
                print("کپچا حل شد:", captcha_text)
                return captcha_text
            elif 'CAPCHA_NOT_READY' in result_response.text:
                print("کپچا هنوز آماده نیست، صبر میکنیم...")
                continue
            else:
                print("خطا در دریافت جواب کپچا:", result_response.text)
                return None
        else:
            print("خطا در تماس با 2Captcha:", result_response.status_code)
            return None
    print("زمان دریافت جواب کپچا به پایان رسید.")
    return None

# ----------- تنظیمات Selenium -----------
CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'  # مسیر کروم درایور شما

options = Options()
options.headless = True  # اگر میخواهید مرورگر باز نشود، این را فعال کنید

service = Service(CHROMEDRIVER_PATH)

def login_and_get_cookies():
    global cookie_string
    driver = webdriver.Chrome(service=service, options=options)
    try:
        driver.get("https://az12.hrtc.ir/hrt/profile/")
        wait = WebDriverWait(driver, 10)

        csrf_token_input = wait.until(EC.presence_of_element_located((By.NAME, 'csrfmiddlewaretoken')))
        csrf_token = csrf_token_input.get_attribute('value')
        print("CSRF Token:", csrf_token)

        national_code_input = driver.find_element(By.ID, 'id_national_code')
        national_code_input.send_keys('0520525264')  # کد ملی خودتون

        track_code_input = driver.find_element(By.ID, 'id_track_code')
        track_code_input.send_keys('8777426094')  # کد رهگیری خودتون

        captcha_img = driver.find_element(By.CSS_SELECTOR, 'img.captcha')

        captcha_image_path = 'captcha.png'
        captcha_img.screenshot(captcha_image_path)
        print(f"تصویر کپچا ذخیره شد: {captcha_image_path}")

        captcha_text = solve_captcha_2captcha(captcha_image_path)
        if not captcha_text:
            print("حل کپچا ناموفق بود، لطفا دستی وارد کنید:")
            captcha_text = input("کد کپچا: ")

        captcha_input = driver.find_element(By.ID, 'id_captcha_1')
        captcha_input.send_keys(captcha_text)

        submit_btn = driver.find_element(By.ID, 'submit-id-submit')
        submit_btn.click()

        time.sleep(5)
        print("فرم ارسال شد. آدرس فعلی:", driver.current_url)

        selenium_cookies = driver.get_cookies()
        cookie_string = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in selenium_cookies])
        print("کوکی‌ها:", cookie_string)

    finally:
        driver.quit()

# لاگین اولیه و گرفتن کوکی‌ها
login_and_get_cookies()

cookies = {item.split("=")[0].strip(): item.split("=")[1].strip() for item in cookie_string.split(";")}

expiry_time = datetime.now() + timedelta(hours=18)
expiry_time_formatted = expiry_time.strftime("%a, %d %b %Y %H:%M:%S GMT")
if "sessionid" in cookies:
    cookies["sessionid"] += f"; Expires={expiry_time_formatted}"

url = "https://az12.hrtc.ir/hrt/pl/home/"
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Sec-Ch-Ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

def get_current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def send_sms():
    sms_url = "https://api.sms.ir/v1/send/bulk"
    payload = {
        "lineNumber": 30007732003728,
        "messageText": "جواب نهایی اومد",
        "mobiles": [
            "+989189561009",
            "+989383734216",
            "+989108663748",
            "+989940715285",
            "+989188872523",
            "+989389354268",
            "+989999371232"
        ],
        "sendDateTime": None
    }
    sms_headers = {
        'X-API-KEY': 'CYSZ6awyphlQemyp7zztiqwnIxr3qzi54UC1VMcenxdc1U40',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(sms_url, json=payload, headers=sms_headers)
        print(f"📩 پیامک ارسال شد: {response.text} - {get_current_timestamp()}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ خطا در ارسال پیامک: {e} - {get_current_timestamp()}")

def display_image_in_terminal(image_path):
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, "success.png")
        img = Image.open(image_path)
        img = img.resize((50, 25))
        img = img.convert("L")
        chars = "@%#*+=-:. "
        ascii_str = "".join(chars[pixel // 25] for pixel in img.getdata())
        ascii_str = "\n".join([ascii_str[i:(i + 50)] for i in range(0, len(ascii_str), 50)])
        print(ascii_str)
    except Exception as e:
        print(f"⚠️ خطا در نمایش تصویر: {e} - {get_current_timestamp()}")

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
                    display_image_in_terminal("success.png")
                    subprocess.run(["open", "-a", "Music"])
                    break
                else:
                    print(f"⏳ هنوز اعلام نتیجه نهایی غیرفعال است... - {get_current_timestamp()}")
                    was_disabled = is_disabled
            else:
                print(f"⚠️ تگ <a> بالای متن 'اعلام نتیجه نهایی' پیدا نشد. - {get_current_timestamp()}")
        else:
            not_found_count += 1
            print(f"❌ متن 'اعلام نتیجه نهایی' پیدا نشد. - {get_current_timestamp()}")
            if not_found_count >= 10:
                print("🔄 ۱۰ بار پیام پیدا نشدن تکرار شد، لاگین مجدد انجام می‌شود...")
                login_and_get_cookies()
                cookies.clear()
                cookies.update({item.split("=")[0].strip(): item.split("=")[1].strip() for item in cookie_string.split(";")})
                not_found_count = 0

    except Exception as e:
        print(f"⚠️ خطا: {e} - {get_current_timestamp()}")
    time.sleep(30)
