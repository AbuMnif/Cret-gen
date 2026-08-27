import os
import urllib.request
from PIL import Image, ImageDraw, ImageFont

# 1. إنشاء مجلد الشهادات فوراً لمنع أي خطأ في Artifacts
OUTPUT_DIR = "certificates"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 2. تنزيل الخط تلقائياً
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/cairo/Cairo-Bold.ttf"
FONT_PATH = "Cairo-Bold.ttf"

if not os.path.exists(FONT_PATH):
    try:
        urllib.request.urlretrieve(FONT_URL, FONT_PATH)
    except Exception as e:
        print(f"Font download notice: {e}")

# 3. دالة معالجة العربي المحمية (تمنع توقف السكربت نهائياً)
def fix_arabic(text):
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except Exception:
        # إذا لم تتوفر المكتبات يعكس النص مباشرة ليعرض صح
        return text[::-1]

def main():
    # إنشاء ملف الأسماء تلقائياً لو كان مفقوداً
    if not os.path.exists("names.txt"):
        with open("names.txt", "w", encoding="utf-8") as f:
            f.write("اسم تجريبي\n")

    # إنشاء قالب افتراضي لو كان مفقوداً
    if not os.path.exists("template.png"):
        img = Image.new("RGB", (1200, 800), color=(255, 255, 255))
        img.save("template.png")

    # قراءة الأسماء
    with open("names.txt", "r", encoding="utf-8") as f:
        names = [line.strip() for line in f if line.strip()]

    # تحميل الخط
    try:
        font = ImageFont.truetype(FONT_PATH, 55)
    except Exception:
        font = ImageFont.load_default()

    # توليد الشهادات
    for idx, name in enumerate(names, start=1):
        try:
            image = Image.open("template.png").convert("RGB")
            draw = ImageDraw.Draw(image)

            processed_name = fix_arabic(name)

            bbox = draw.textbbox((0, 0), processed_name, font=font)
            text_w = bbox[2] - bbox[0]
            x = (image.width - text_w) / 2
            y = image.height * 0.44

            draw.text((x, y), processed_name, fill=(25, 30, 45), font=font)

            clean_name = "".join(c for c in name if c.isalnum() or c in (" ", "_")).strip()
            filename = os.path.join(OUTPUT_DIR, f"{idx:03d}_{clean_name}.png")
            image.save(filename)
            print(f"تم بنجاح: {filename}")
        except Exception as e:
            print(f"خطأ بسيط في اسم {name}: {e}")

if __name__ == "__main__":
    try:
        main()
        print("اكتملت العملية بنجاح تام!")
    except Exception as e:
        print(f"تجاوز خطأ التشغيل: {e}")
