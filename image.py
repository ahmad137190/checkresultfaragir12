import os, re
from PIL import Image, ImageOps, ImageFilter
import pytesseract

def normalize(text: str) -> str:
    text = text.replace('x', '*').replace('X', '*').replace('×', '*')
    text = re.sub(r'[=≥<>].*$', '', text)
    return text.strip()

def is_safe_expression(expr: str) -> bool:
    return re.fullmatch(r'\d+[\+\-\*/]\d+', expr) is not None

def solve_captcha(image_filename):
    if not os.path.isfile(image_filename):
        return f"فایل '{image_filename}' در کنار h.py پیدا نشد."

    img = Image.open(image_filename)
    gray = img.convert('L')
    contrast = ImageOps.autocontrast(gray)
    binary = contrast.point(lambda x: 0 if x < 140 else 255, '1')
    clean_img = binary.filter(ImageFilter.MedianFilter(3))

    raw_text = pytesseract.image_to_string(clean_img, config='--psm 7')
    text = normalize(raw_text)

    print("clean:", text)  # برای دیباگ

    if not is_safe_expression(text):
        return "خطا در تشخیص کپچا"

    try:
        return str(eval(text))
    except Exception as e:
        return f"خطا در محاسبه: {e}"

if __name__ == "__main__":
    print(solve_captcha("captcha.png"))
