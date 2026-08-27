import os
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

# --- مسار الخط العربي المحلي (El Messiri) ---
FONT_PATH = "Font.ttf"

# --- دالة تصحيح النص العربي ---
def process_text(text):
    """
    تقوم بتشكيل النص العربي ثم عكس ترتيب الأحرف ليعرض من اليمين إلى اليسار.
    """
    reshaped_text = arabic_reshaper.reshape(text)    # لتوصيل الأحرف ببعضها
    bidi_text = get_display(reshaped_text)        # لعكس النص لليمين-اليسار
    return bidi_text

# --- الدالة الرئيسية ---
def main():
    # مجلد المخرجات
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

    # 2. تحميل الخط المحلي Font.ttf
    try:
        font = ImageFont.truetype(FONT_PATH, 55)
    except OSError:
        print(f"خطأ: لم يتم العثور على ملف الخط باسم {FONT_PATH} في المجلد!")
        return

    # 3. معالجة كل اسم وتوليد الشهادة له
    for idx, name in enumerate(names, start=1):
        try:
            image = Image.open("template.png").convert("RGB")
        except FileNotFoundError:
            print("خطأ: لم يتم العثور على ملف template.png في المستودع!")
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

        # هـ. تنظيف الاسم لاستخدامه كاسم للملف
        clean_name = "".join(
            c for c in name if c.isalnum() or c in (" ", "_")
        ).strip()
        
        # و. حفظ الشهادة
        filename = f"{output_dir}/{idx:03d}_{clean_name}.png"
        image.save(filename)
        print(f"تم توليد شهادة لـ: {name} (الملف: {filename})")

if __name__ == "__main__":
    main()
