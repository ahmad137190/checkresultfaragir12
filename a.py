import requests
from bs4 import BeautifulSoup
import time
import subprocess
import json
from PIL import Image
from datetime import datetime, timedelta
import os

# تابع برای گرفتن تاریخ و زمان کنونی
def get_current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# محاسبه زمان انقضای جدید (۱۴ ساعت از حالا)
expiry_time = datetime.now() + timedelta(hours=18)
expiry_time_formatted = expiry_time.strftime("%a, %d %b %Y %H:%M:%S GMT")

# رشته کوکی‌ها
cookie_string = "_ga=GA1.1.177117572.1745664028; csrftoken=WMP2Xmc572WnOHOd0zFM1HM3prWkLucTPFt06pAaGMXEqqhUSbRoaxB3QkKkNeNQ; __arcsjs=99a600454aa0a148e4dfc0ca69e95432; sessionid=na2sztqpqto4ilzx4l55qgu01faqlsd8; _ga_VC3V6PM6FB=GS2.1.s1748259429$o55$g1$t1748259502$j0$l0$h0"

# تبدیل رشته به دیکشنری
cookies = {item.split("=")[0].strip(): item.split("=")[1].strip() for item in cookie_string.split(";")}

# تنظیم زمان انقضای کوکی sessionid
cookies["sessionid"] += f"; Expires={expiry_time_formatted}"

# درخواست اصلی
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

# تابع ارسال پیامک
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

# تابع نمایش تصویر در ترمینال
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

# اجرای حلقه بررسی
was_disabled = True
while True:
    try:
        response = requests.get(url, headers=headers, cookies=cookies)
        soup = BeautifulSoup(response.text, "html.parser")
        target_p = soup.find("p", string="اعلام نتیجه نهایی")
        if target_p:
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
            print(f"❌ متن 'اعلام نتیجه نهایی' پیدا نشد. - {get_current_timestamp()}")
    except Exception as e:
        print(f"⚠️ خطا: {e} - {get_current_timestamp()}")
    time.sleep(30)
