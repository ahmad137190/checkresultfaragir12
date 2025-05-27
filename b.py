from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# مسیر chromedriver که دانلود کردید
CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'

# تنظیمات کروم (می‌توانید headless هم بگذارید)
options = Options()
# options.headless = True  # اگر می‌خواهید مرورگر باز نشود، uncomment کنید

service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

try:
    driver.get("https://az12.hrtc.ir/hrt/profile/")

    time.sleep(5)  # کمی صبر برای بارگذاری صفحه

    # گرفتن csrfmiddlewaretoken (اگر لازم است، در این فرم بصورت hidden input هست)
    csrf_token = driver.find_element(By.NAME, 'csrfmiddlewaretoken').get_attribute('value')
    print("CSRF Token:", csrf_token)

    # پر کردن فیلد کد ملی
    national_code_input = driver.find_element(By.ID, 'id_national_code')
    national_code_input.send_keys('0520525264')  # کد ملی خودتان را اینجا بگذارید

    # پر کردن کد رهگیری (اگر دارید)
    track_code_input = driver.find_element(By.ID, 'id_track_code')
    track_code_input.send_keys('8777426094')  # کد رهگیری خودتان را اینجا بگذارید

    # کپچا باید دستی وارد شود، پس ابتدا تصویر کپچا را مشاهده کنید
    captcha_img = driver.find_element(By.CSS_SELECTOR, 'img.captcha')
    captcha_src = captcha_img.get_attribute('src')
    print("آدرس تصویر کپچا:", captcha_src)
    print("لطفا کپچا را ببینید و جواب آن را در ترمینال وارد کنید:")

    captcha_value = input("کد کپچا: ")

    captcha_input = driver.find_element(By.ID, 'id_captcha_1')
    captcha_input.send_keys(captcha_value)

    # ارسال فرم
    submit_btn = driver.find_element(By.ID, 'submit-id-submit')
    submit_btn.click()

    time.sleep(5)  # صبر کنید تا صفحه بعد لود شود و ببینید وارد شدید یا نه

    print("فرم ارسال شد. آدرس فعلی:", driver.current_url)

finally:
    driver.quit()
