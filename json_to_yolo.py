import json
import os

# JSON dosyasının yolu
json_path = "cleaned_annotations.json"  # JSON dosyanın yolunu burada belirt
output_dir = "labels/"  # YOLO formatında etiketlerin kaydedileceği klasör
image_dir = "final_images/"  # Resimlerin bulunduğu klasör

# Klasörleri oluştur
os.makedirs(output_dir, exist_ok=True)

# JSON dosyasını aç
with open(json_path, "r") as f:
    coco_data = json.load(f)

# ID -> Dosya adı eşlemesi
image_id_to_filename = {img["id"]: img["file_name"] for img in coco_data["images"]}

# ID -> Kategori adı eşlemesi
category_mapping = {category["id"]: category["name"] for category in coco_data["categories"]}

# Tüm görüntüler için anotasyonları oluştur
for ann in coco_data["annotations"]:
    image_id = ann["image_id"]

    # Eğer bu `image_id`, `images` içinde yoksa atla
    if image_id not in image_id_to_filename:
        print(f"Uyarı: {image_id} ID'li resim JSON'da yok, atlanıyor.")
        continue

    file_name = image_id_to_filename[image_id]
    width, height = 640, 640  # JSON'da sabit görünüyor, dinamik hale getirebilirsin

    category_id = ann["category_id"]  # -1 çıkartmaya gerek yok çünkü ID 0'dan başlıyor
    x_min, y_min, bbox_w, bbox_h = ann["bbox"]

    # YOLO formatına çevir (normalizasyon)
    x_center = (x_min + bbox_w / 2) / width
    y_center = (y_min + bbox_h / 2) / height
    bbox_w /= width
    bbox_h /= height

    # Çıkış dosyasını oluştur
    txt_file = os.path.join(output_dir, file_name.replace(".png", ".txt"))

    # `.txt` dosyasına yaz
    with open(txt_file, "a") as f:
        f.write(f"{category_id} {x_center:.6f} {y_center:.6f} {bbox_w:.6f} {bbox_h:.6f}\n")
