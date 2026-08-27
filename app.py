import os
import urllib.request
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

# --- تحميل الخط العربي تلقائياً ---
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/tajawal/Tajawal-Bold.ttf"
FONT_PATH = "Tajawal-Bold.ttf"

if not os.path.exists(FONT_PATH):
    print("تنزيل الخط...")
    try:
        urllib.request.urlretrieve(FONT_URL, FONT_PATH)
    except Exception as e:
        print(f"خطأ في تنزيل الخط: {e}")
        # إذا فشل التنزيل، نحاول استخدام خط نظام احتياطي، لكنه لن يكون Tajawal
        FONT_PATH = "DejaVuSans.ttf" 

# --- دالة تصحيح النص العربي (الخطوة الأهم) ---
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
    # تأكد من أن ملف الأسماء لديك اسمه 'names.txt'
    with open("names.txt", "r", encoding="utf-8") as f:
        names = [line.strip() for line in f if line.strip()]

    if not names:
        print("ملف names.txt فارغ!")
        return

    # 2. تحديد نوع الخط وحجمه
    # حجم الخط 55 مناسب، إذا أردته أصغر قم بتقليل الرقم (مثلا 45)
    font = ImageFont.truetype(FONT_PATH, 55)

    # 3. معالجة كل اسم وتوليد الشهادة له
    for idx, name in enumerate(names, start=1):
        # فتح القالب (تأكد أن اسمه template.png)
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

        # ج. التوسيط الأفقي ومكان الارتفاع (الارتفاع معدل ليناسب القالب)
        x = (image.width - text_w) / 2
        y = image.height * 0.44  # تحكم في مكان الارتفاع من هنا (0.0 لأعلى و 1.0 لأسفل)

        # د. كتابة الاسم على الصورة بلون داكن
        # اللون (25, 30, 45) هو لون أسود داكن مشابه للخطوط الأصلية
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
