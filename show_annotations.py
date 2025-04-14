import json
import os
from PIL import Image, ImageDraw

# JSON dosyanın yolu
ANNOTATIONS_FILE = "annotations.json"

# Görüntülerin bulunduğu klasör
IMAGE_DIR = "images/test/"  # 📌 Burayı kendi dosya konumuna göre güncelle!

# Bounding Box'lı resimlerin kaydedileceği klasör
OUTPUT_DIR = "output_with_bbox/"
os.makedirs(OUTPUT_DIR, exist_ok=True)  # Klasör yoksa oluştur

# JSON dosyasını aç
with open(ANNOTATIONS_FILE, "r") as f:
    coco_data = json.load(f)

# Görüntü bilgilerini ve bbox'ları al
images_info = {img["id"]: img["file_name"] for img in coco_data["images"]}
annotations = coco_data["annotations"]

# Her görüntü için bounding box'ları çiz
for image_id, file_name in images_info.items():
    image_path = os.path.join(IMAGE_DIR, file_name)
    
    if not os.path.exists(image_path):
        print(f"❌ Uyarı: {image_path} bulunamadı, atlanıyor...")
        continue  # Dosya yoksa bu görseli geç
    
    # 📌 Görseli aç
    image = Image.open(image_path).convert("RGBA")
    draw = ImageDraw.Draw(image)

    # 📌 Bu resme ait tüm bounding box'ları al
    for ann in annotations:
        if ann["image_id"] == image_id:
            x, y, w, h = ann["bbox"]  # Bounding Box koordinatları
            draw.rectangle([x, y, x + w, y + h], outline="red", width=3)
            draw.text((x, y - 10), f"C_ID: {ann['category_id']}", fill="red")

    # 📌 Bounding Box eklenmiş görüntüyü kaydet
    output_path = os.path.join(OUTPUT_DIR, file_name)
    image.save(output_path)

    # 📌 Bounding Box'lı görüntüyü göster
    image.show()

print(f"✅ Bounding Box'lı görüntüler {OUTPUT_DIR} klasörüne kaydedildi.")
