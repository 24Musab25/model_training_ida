import os
import shutil
import random

# 📌 Mevcut veri setinin bulunduğu ana klasör
image_dir = "final_images/"
label_dir = "labels/"

# 📌 Yeni oluşturulacak Train, Val, Test klasörleri
train_img_dir = "final_images/train/"
val_img_dir = "final_images/val/"
test_img_dir = "final_images/test/"

train_lbl_dir = "labels/train/"
val_lbl_dir = "labels/val/"
test_lbl_dir = "labels/test/"

# 📌 Klasörleri oluştur
os.makedirs(train_img_dir, exist_ok=True)
os.makedirs(val_img_dir, exist_ok=True)
os.makedirs(test_img_dir, exist_ok=True)

os.makedirs(train_lbl_dir, exist_ok=True)
os.makedirs(val_lbl_dir, exist_ok=True)
os.makedirs(test_lbl_dir, exist_ok=True)

# 📌 Tüm resimleri listele ve rastgele sırala
images = sorted([f for f in os.listdir(image_dir) if f.endswith((".png", ".jpg"))])
random.shuffle(images)

# 📌 Train, Val ve Test için ayırma oranları
train_split = int(len(images) * 0.7)  # %70 Train
val_split = int(len(images) * 0.9)    # %20 Validation, %10 Test

train_files = images[:train_split]
val_files = images[train_split:val_split]
test_files = images[val_split:]

# 📌 Train klasörüne taşı
for file in train_files:
    shutil.move(os.path.join(image_dir, file), train_img_dir)
    shutil.move(os.path.join(label_dir, file.replace(".png", ".txt").replace(".jpg", ".txt")), train_lbl_dir)

# 📌 Validation klasörüne taşı
for file in val_files:
    shutil.move(os.path.join(image_dir, file), val_img_dir)
    shutil.move(os.path.join(label_dir, file.replace(".png", ".txt").replace(".jpg", ".txt")), val_lbl_dir)

# 📌 Test klasörüne taşı
for file in test_files:
    shutil.move(os.path.join(image_dir, file), test_img_dir)
    shutil.move(os.path.join(label_dir, file.replace(".png", ".txt").replace(".jpg", ".txt")), test_lbl_dir)

print("✅ Train/Validation/Test ayrımı tamamlandı!")
