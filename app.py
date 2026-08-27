import os
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

# --- مسار الخط العربي المحلي ---
FONT_PATH = "Font.ttf"

# --- دالة تصحيح النص العربي (المعدلة لمنع عكس الأحرف) ---
def process_text(text):
    # إعدادات مخصصة لمشكل تشكيل الحروف العربية
    configuration = {
        'delete_harakat': False,
        'support_ligatures': False  # إيقاف التجميع المعقد الذي يسبب عكس الاتجاه
    }
    reshaper = arabic_reshaper.ArabicReshaper(configuration)
    reshaped_text = reshaper.reshape(text)
    
    # استخدام base_dir='RTL' لضمان فرض اتجاه النص من اليمين إلى اليسار
    bidi_text = get_display(reshaped_text, base_dir='RTL')
    return bidi_text

# --- الدالة الرئيسية ---
def main():
    output_dir = "certificates"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. فتح ملف الأسماء
    try:
        with open("names.txt", "r", encoding="utf-8") as f:
            names = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("خطأ: لم يتم العثور على ملف names.txt!")
        return

    if not names:
        print("ملف names.txt فارغ!")
        return

    # 2. تحميل الخط المحلي
    try:
        font = ImageFont.truetype(FONT_PATH, 55)
    except OSError:
        print(f"خطأ: لم يتم العثور على ملف الخط باسم {FONT_PATH}!")
        return

    # 3. معالجة كل اسم وتوليد الشهادة
    for idx, name in enumerate(names, start=1):
        try:
            image = Image.open("template.png").convert("RGB")
        except FileNotFoundError:
            print("خطأ: لم يتم العثور على ملف template.png!")
            return
        
        draw = ImageDraw.Draw(image)

        # أ. معالجة الاسم العربي
        processed_name = process_text(name)

        # ب. حساب عرض النص للتوسيط
        bbox = draw.textbbox((0, 0), processed_name, font=font)
        text_w = bbox[2] - bbox[0]

        # ج. التوسيط الأفقي ومكان الارتفاع
        x = (image.width - text_w) / 2
        y = image.height * 0.44  

        # د. كتابة الاسم على الصورة
        draw.text((x, y), processed_name, fill=(25, 30, 45), font=font)

        # هـ. تنظيف الاسم لحفظ الملف
        clean_name = "".join(
            c for c in name if c.isalnum() or c in (" ", "_")
        ).strip()
        
        # و. حفظ الشهادة
        filename = f"{output_dir}/{idx:03d}_{clean_name}.png"
        image.save(filename)
        print(f"تم توليد شهادة لـ: {name}")

if __name__ == "__main__":
    main()
