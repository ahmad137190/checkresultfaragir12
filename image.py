from PIL import Image
import pytesseract
import re

def solve_captcha(image_path):
    # خواندن تصویر
    image = Image.open(image_path)

    # استفاده از OCR برای استخراج متن
    text = pytesseract.image_to_string(image, config='--psm 7')  # حالت 7 فقط یک خط را می‌خواند

    # استخراج عدد و عملگر
    match = re.match(r'(\d+)\s*([+*/-])\s*(\d+)', text)
    if not match:
        return "خطا در تشخیص کپچا"

    a, op, b = match.groups()
    a, b = int(a), int(b)

    # محاسبه نتیجه
    if op == '+':
        result = a + b
    elif op == '-':
        result = a - b
    elif op == '*':
        result = a * b
    elif op == '/':
        result = a / b
    else:
        return "عملگر نامشخص"

    return str(result)

# تست تابع
if __name__ == "__main__":
    result = solve_captcha("captcha.png")
    print("پاسخ کپچا:", result)
