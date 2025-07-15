import os
from PIL import Image, ImageOps

SOURCE_DIR = "images/predict_facing_test/right"
DEST_DIR = "images/predict_facing_test/left"

os.makedirs(DEST_DIR, exist_ok=True)

count = 0
for filename in os.listdir(SOURCE_DIR):
    if not filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        continue

    source_path = os.path.join(SOURCE_DIR, filename)
    dest_filename = os.path.splitext(filename)[0] + "_flipped.png"
    dest_path = os.path.join(DEST_DIR, dest_filename)

    try:
        image = Image.open(source_path).convert("RGBA")
        flipped = ImageOps.mirror(image)
        flipped.save(dest_path)
        print(f"✅ Copied and flipped: {filename} → {dest_filename}")
        count += 1
    except Exception as e:
        print(f"❌ Error processing {filename}: {e}")

print(f"\n📦 Total images flipped and saved: {count}")
