import os
import urllib.request
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

# --- تحميل خط "القاهرة" العريض (Cairo Bold) تلقائياً ---
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/cairo/Cairo-Bold.ttf"
FONT_PATH = "Cairo-Bold.ttf"

def load_font(font_size=55):
    if not os.path.exists(FONT_PATH):
        print("جاري تنزيل الخط الرسمي...")
        try:
            urllib.request.urlretrieve(FONT_URL, FONT_PATH)
        except Exception as e:
            print(f"فشل تنزيل الخط: {e}")
            return None
    return ImageFont.truetype(FONT_PATH, font_size)

# --- الدالة السحرية لتصحيح العربي 100% ---
def process_text(text):
    # 1. إعدادات لإجبار التشكيل والتوصيل الصحيح
    configuration = {
        'delete_harakat': False,
        'support_ligatures': True
    }
    reshaper = arabic_reshaper.ArabicReshaper(configuration)
    reshaped_text = reshaper.reshape(text)
    
    # 2. تطبيق خوارزمية الاتجاه مع تقسيم وتعديل الكلمات
    bidi_text = get_display(reshaped_text)
    
    # 3. عكس ترتيب الكلمات فقط لتظهر من اليمين لليسار بالشكل الصحيح في Pillow
    words = bidi_text.split(" ")
    correct_arabic = " ".join(words[::-1])
    
    return correct_arabic

# --- الدالة الرئيسية ---
def main():
    output_dir = "certificates"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        with open("names.txt", "r", encoding="utf-8") as f:
            names = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("خطأ: لم يتم العثور على ملف names.txt!")
        return

    if not names:
        print("ملف names.txt فارغ!")
        return

    font = load_font(55)
    if font is None:
        return

    for idx, name in enumerate(names, start=1):
        try:
            image = Image.open("template.png").convert("RGB")
        except FileNotFoundError:
            print("خطأ: لم يتم العثور على ملف template.png!")
            return
        
        draw = ImageDraw.Draw(image)

        # معالجة النص
        processed_name = process_text(name)

        # حساب التوسيط
        bbox = draw.textbbox((0, 0), processed_name, font=font)
        text_w = bbox[2] - bbox[0]

        x = (image.width - text_w) / 2
        y = image.height * 0.44  

        # كتابة الاسم
        draw.text((x, y), processed_name, fill=(25, 30, 45), font=font)

        # حفظ الملف
        clean_name = "".join(c for c in name if c.isalnum() or c in (" ", "_")).strip()
        filename = f"{output_dir}/{idx:03d}_{clean_name}.png"
        image.save(filename)
        print(f"تم توليد شهادة لـ: {name}")

if __name__ == "__main__":
    main()
