import requests
from bs4 import BeautifulSoup
import time
import subprocess
import json

# رشته کوکی‌ها
cookie_string = "_ga=GA1.1.177117572.1745664028; csrftoken=WMP2Xmc572WnOHOd0zFM1HM3prWkLucTPFt06pAaGMXEqqhUSbRoaxB3QkKkNeNQ; __arcsjs=e638c4aab156162a467e3b7c402e8576; sessionid=l2exhenhogmksy0t9pofq6pk6rng2v03; _ga_VC3V6PM6FB=GS2.1.s1748169258$o49$g1$t1748169351$j0$l0$h0"

# تبدیل رشته به دیکشنری
cookies = {item.split("=")[0].strip(): item.split("=")[1].strip() for item in cookie_string.split(";")}

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

def send_sms():
    url = "https://api.sms.ir/v1/send/bulk"
    payload = {
        "lineNumber": 30007732003728,
        "messageText": " جواب نهایی اومد",
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
    headers = {
        'X-API-KEY': 'CYSZ6awyphlQemyp7zztiqwnIxr3qzi54UC1VMcenxdc1U40',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"📩 پیامک ارسال شد: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ خطا در ارسال پیامک: {e}")

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
                    print("✅ اعلام نتیجه نهایی فعال شد!")
                    send_sms()  # ارسال پیامک
                    subprocess.run(["open", "-a", "Music"])  # پخش موسیقی
                    break
                else:
                    print("⏳ هنوز اعلام نتیجه نهایی غیرفعال است...")
                    #send_sms()  # ارسال پیامک در حالت غیرفعال
                    was_disabled = is_disabled
            else:
                print("⚠️ تگ <a> بالای متن 'اعلام نتیجه نهایی' پیدا نشد.")
        else:
            print("❌ متن 'اعلام نتیجه نهایی' پیدا نشد.")
    except Exception as e:
        print(f"⚠️ خطا: {e}")
    time.sleep(120)
