import os
import sys
import urllib.request
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

# --- إنشاء مجلد المخرجات فوراً لمنع فشل GitHub Actions ---
OUTPUT_DIR = "certificates"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- تحميل الخط العربي الرسمي (Cairo-Bold) ---
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/cairo/Cairo-Bold.ttf"
FONT_PATH = "Cairo-Bold.ttf"

def load_font(font_size=55):
    if not os.path.exists(FONT_PATH):
        print("جاري تنزيل الخط...")
        try:
            urllib.request.urlretrieve(FONT_URL, FONT_PATH)
            print("تم تنزيل الخط بنجاح.")
        except Exception as e:
            print(f"فشل تنزيل الخط: {e}")
            return None
    return ImageFont.truetype(FONT_PATH, font_size)

# --- دالة تصحيح النص العربي ---
def process_text(text):
    try:
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        words = bidi_text.split(" ")
        return " ".join(words[::-1])
    except Exception as e:
        print(f"خطأ في معالجة الاسم ({text}): {e}")
        return text

# --- الدالة الرئيسية ---
def main():
    print("شروع تنفيذ السكربت...")

    # 1. التثبت من وجود الملفات الأساسية
    if not os.path.exists("names.txt"):
        print("خطأ فادح: ملف names.txt غير موجود في المستودع!")
        sys.exit(1)

    if not os.path.exists("template.png"):
        print("خطأ فادح: ملف template.png غير موجود في المستودع!")
        sys.exit(1)

    # 2. قراءة الأسماء
    with open("names.txt", "r", encoding="utf-8") as f:
        names = [line.strip() for line in f if line.strip()]

    if not names:
        print("خطأ: ملف names.txt فارغ!")
        sys.exit(1)

    print(f"تم العثور على {len(names)} اسم.")

    # 3. تحميل الخط
    font = load_font(55)
    if font is None:
        print("خطأ: تعذر تحميل الخط.")
        sys.exit(1)

    # 4. توليد الشهادات
    generated_count = 0
    for idx, name in enumerate(names, start=1):
        try:
            image = Image.open("template.png").convert("RGB")
            draw = ImageDraw.Draw(image)

            processed_name = process_text(name)

            bbox = draw.textbbox((0, 0), processed_name, font=font)
            text_w = bbox[2] - bbox[0]

            x = (image.width - text_w) / 2
            y = image.height * 0.44  

            draw.text((x, y), processed_name, fill=(25, 30, 45), font=font)

            clean_name = "".join(c for c in name if c.isalnum() or c in (" ", "_")).strip()
            filename = os.path.join(OUTPUT_DIR, f"{idx:03d}_{clean_name}.png")
            image.save(filename)
            
            print(f"تم إنشاء: {filename}")
            generated_count += 1
        except Exception as e:
            print(f"خطأ أثناء إنشاء شهادة {name}: {e}")

    print(f"إجمالي الشهادات المكتملة: {generated_count}")

if __name__ == "__main__":
    main()
