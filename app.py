import os
import sys
import urllib.request
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

# إنشاء مجلد المخرجات فوراً
OUTPUT_DIR = "certificates"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# تنزيل خط القاهرة العريض
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/cairo/Cairo-Bold.ttf"
FONT_PATH = "Cairo-Bold.ttf"

def load_font(font_size=55):
    if not os.path.exists(FONT_PATH):
        try:
            urllib.request.urlretrieve(FONT_URL, FONT_PATH)
        except Exception as e:
            print(f"Error downloading font: {e}")
            return None
    return ImageFont.truetype(FONT_PATH, font_size)

def process_text(text):
    try:
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        words = bidi_text.split(" ")
        return " ".join(words[::-1])
    except Exception:
        return text

def main():
    if not os.path.exists("names.txt") or not os.path.exists("template.png"):
        print("Error: names.txt or template.png is missing!")
        sys.exit(1)

    with open("names.txt", "r", encoding="utf-8") as f:
        names = [line.strip() for line in f if line.strip()]

    if not names:
        print("Error: names.txt is empty!")
        sys.exit(1)

    font = load_font(55)
    if font is None:
        sys.exit(1)

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
            print(f"Generated: {filename}")
        except Exception as e:
            print(f"Error processing {name}: {e}")

if __name__ == "__main__":
    main()
