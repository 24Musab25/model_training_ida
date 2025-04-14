import json
import os
from collections import defaultdict

def is_bbox_overlapping(box1, box2):
    """
    İki bounding box çakışıyor mu?
    box1 ve box2, [x, y, width, height] formatındadır.
    """
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2

    # Bbox'lardan sol üst ve sağ alt köşeleri bul
    x1_max = x1 + w1
    y1_max = y1 + h1
    x2_max = x2 + w2
    y2_max = y2 + h2

    # Kesişim alanı hesapla
    inter_x1 = max(x1, x2)
    inter_y1 = max(y1, y2)
    inter_x2 = min(x1_max, x2_max)
    inter_y2 = min(y1_max, y2_max)

    # Eğer kesişim varsa (inter_width ve inter_height > 0)
    inter_width = inter_x2 - inter_x1
    inter_height = inter_y2 - inter_y1

    return inter_width > 0 and inter_height > 0  # True = Çakışma var, False = Çakışma yok

# JSON dosyasını oku
with open("annotations.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# `image_id`'ye göre annotations'ları grupla
grouped_annotations = defaultdict(list)
for annotation in data["annotations"]:
    grouped_annotations[annotation["image_id"]].append(annotation)

# Çakışan resim ID'lerini tutacak set
overlapping_image_ids = set()

# Her image_id için bbox'ları karşılaştır ve çakışmaları bul
for image_id, annotations in grouped_annotations.items():
    num_annotations = len(annotations)

    # Bbox'ları karşılaştır
    for i in range(num_annotations):
        for j in range(i + 1, num_annotations):
            bbox1 = annotations[i]["bbox"]
            bbox2 = annotations[j]["bbox"]

            if is_bbox_overlapping(bbox1, bbox2):
                print(f"Çakışma tespit edildi! Image ID: {image_id}")
                overlapping_image_ids.add(image_id)

# Çakışma olan image_id'leri yazdır
if overlapping_image_ids:
    print(f"\nÇakışma tespit edilen image_id'ler: {sorted(overlapping_image_ids)}")

    # Çakışan `image_id`'lere sahip annotation'ları temizle
    data["annotations"] = [ann for ann in data["annotations"] if ann["image_id"] not in overlapping_image_ids]

    # Çakışan `image_id`'ye sahip resimleri de temizle
    images_to_delete = [img for img in data["images"] if img["id"] in overlapping_image_ids]

    # Klasörden resimleri silme işlemi
    image_folder = "final_images"  # Resimlerin bulunduğu klasör
    for img in images_to_delete:
        image_path = os.path.join(image_folder, img["file_name"])
        if os.path.exists(image_path):  # Dosya var mı kontrol et
            os.remove(image_path)
            print(f"{image_path} silindi.")
        else:
            print(f"{image_path} bulunamadı.")

    # JSON'dan çakışan resimleri de temizle
    data["images"] = [img for img in data["images"] if img["id"] not in overlapping_image_ids]

    # Güncellenmiş JSON'u kaydet
    with open("cleaned_annotations.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    print("\nÇakışan image_id'ler, ilgili annotations ve klasördeki resimler silindi, yeni JSON kaydedildi.")
else:
    print("\nHiç çakışma tespit edilmedi.")
