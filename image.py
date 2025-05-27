import os
from PIL import Image, ImageOps, ImageFilter
import pytesseract
import re

def solve_captcha(image_filename):
    # بررسی وجود فایل در مسیر جاری
    if not os.path.isfile(image_filename):
        return f"فایل '{image_filename}' در کنار فایل h.py پیدا نشد."

    # بارگذاری تصویر
    image = Image.open(image_filename)

    # پیش‌پردازش تصویر
    gray_image = image.convert('L')
    enhanced_image = ImageOps.autocontrast(gray_image)
    binary_image = enhanced_image.point(lambda x: 0 if x < 140 else 255, '1')
    denoised_image = binary_image.filter(ImageFilter.MedianFilter(size=3))

    # استخراج متن از تصویر
    text = pytesseract.image_to_string(denoised_image, config='--psm 7')

    # تطبیق با عبارت ریاضی
    match = re.search(r'(\d+)\s*([+*/-])\s*(\d+)', text)
    if not match:
        return "خطا در تشخیص کپچا"

    a, op, b = match.groups()
    a, b = int(a), int(b)

    try:
        if op == '+':
            return str(a + b)
        elif op == '-':
            return str(a - b)
        elif op == '*':
            return str(a * b)
        elif op == '/':
            return str(a / b)
        else:
            return "عملگر نامشخص"
    except Exception as e:
        return f"خطا در محاسبه: {str(e)}"

# اجرای مستقیم فایل
if __name__ == "__main__":
    print(solve_captcha("captcha.png"))
