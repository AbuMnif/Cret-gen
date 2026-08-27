import os
import urllib.request
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont

# تحميل الخط العربي تلقائياً
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/tajawal/Tajawal-Bold.ttf"
FONT_PATH = "Tajawal-Bold.ttf"

if not os.path.exists(FONT_PATH):
    urllib.request.urlretrieve(FONT_URL, FONT_PATH)


def process_text(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


def main():
    output_dir = "certificates"
    os.makedirs(output_dir, exist_ok=True)

    # حجم الخط مناسب تماماً للفراغ بين للطلب والسطر التالي
    font = ImageFont.truetype(FONT_PATH, 55)

    with open("names.txt", "r", encoding="utf-8") as f:
        names = [line.strip() for line in f if line.strip()]

    for idx, name in enumerate(names, start=1):
        image = Image.open("template.png").convert("RGB")
        draw = ImageDraw.Draw(image)

        processed_name = process_text(name)
        bbox = draw.textbbox((0, 0), processed_name, font=font)
        text_w = bbox[2] - bbox[0]

        # التوسيط الأفقي
        x = (image.width - text_w) / 2

        # موضع الارتفاع: تحكمنا به ليكون تحت كلمة "للطالب" مباشرة (عند 44% من ارتفاع الصورة)
        y = image.height * 0.44

        # كتابة النص باللون الأسود الشبه غامق مثل خط الشهادة
        draw.text((x, y), processed_name, fill=(25, 30, 45), font=font)

        clean_name = "".join(
            c for c in name if c.isalnum() or c in (" ", "_")
        ).strip()
        image.save(f"{output_dir}/{idx:03d}_{clean_name}.png")


if __name__ == "__main__":
    main()
