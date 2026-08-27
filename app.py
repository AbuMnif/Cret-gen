import os
import urllib.request
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

# --- تحميل خط عربي رسمي وعريض (Tajawal Bold) تلقائياً ---
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/tajawal/Tajawal-Bold.ttf"
FONT_PATH = "Tajawal-Bold.ttf"

def load_font(font_size=55):
    """تحميل الخط من الإنترنت إذا لم يكن موجوداً محلياً"""
    if not os.path.exists(FONT_PATH):
        print("جاري تنزيل الخط الرسمي (Tajawal Bold)...")
        try:
            # تنزيل الخط مباشرة من مجلد خطوط جوجل
            urllib.request.urlretrieve(FONT_URL, FONT_PATH)
        except Exception as e:
            print(f"فشل تنزيل الخط: {e}")
            return None
    return ImageFont.truetype(FONT_PATH, font_size)

# --- دالة تصحيح النص العربي ---
def process_text(text):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

# --- الدالة الرئيسية ---
def main():
    output_dir = "certificates"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. قراءة الأسماء
    try:
        with open("names.txt", "r", encoding="utf-8") as f:
            names = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("خطأ: لم يتم العثور على ملف names.txt!")
        return

    if not names:
        print("ملف names.txt فارغ!")
        return

    # 2. تجهيز الخط
    font = load_font(55)
    if font is None:
        print("تعذر تحميل الخط، تم إيقاف العملية.")
        return

    # 3. توليد الشهادات
    for idx, name in enumerate(names, start=1):
        try:
            image = Image.open("template.png").convert("RGB")
        except FileNotFoundError:
            print("خطأ: لم يتم العثور على ملف template.png!")
            return
        
        draw = ImageDraw.Draw(image)

        # أ. معالجة الاسم العربي
        processed_name = process_text(name)

        # ب. حساب التوسيط
        bbox = draw.textbbox((0, 0), processed_name, font=font)
        text_w = bbox[2] - bbox[0]

        # ج. مكان الإحداثيات
        x = (image.width - text_w) / 2
        y = image.height * 0.44  

        # د. كتابة الاسم (لون داكن فخم)
        draw.text((x, y), processed_name, fill=(25, 30, 45), font=font)

        # هـ. حفظ الشهادة
        clean_name = "".join(c for c in name if c.isalnum() or c in (" ", "_")).strip()
        filename = f"{output_dir}/{idx:03d}_{clean_name}.png"
        image.save(filename)
        print(f"تم توليد شهادة لـ: {name}")

if __name__ == "__main__":
    main()
