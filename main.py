
from PIL import Image, ImageFilter, ImageDraw
import os
import random
from PIL import Image
import numpy as np
import cv2
import json
import sys
from pathlib import Path
import re


class Main_Process:
    def __init__(self, cfg):
        self.cfg = cfg
        self.bbox_list = []


    
    def make_transparent_and_resize(self, image, image_list, bg_color, tolerance=10):
        """
        - Gri arka planı belirlenen tolerans dahilinde şeffaf yapar.
        - Resmi yeniden boyutlandırır.
        - Orijinal görüntüyü değiştirir.
        """
        width, height = image.size

        original_filename = getattr(image, "filename", None)  # ✅ Orijinal dosya adını koru


        # 🔹 Yeni boyutları belirle (Maksimum 512 piksel)
        new_width = min(random.randint(width // 18, width // 6), 512)
        new_height = min(random.randint(height // 18, height // 6), 512)
        image = image.resize((new_width, new_height), Image.LANCZOS)

        image.filename = original_filename  # ✅ Filename bilgisini geri ekle!


        # **Listeye ekleyerek geri döndür**
        image_list.append(image)
        return image_list
    
    # şu an perspektif dönüşümü birkaç noktayla yapabiliyoruz varyans oluşturacağız 
    def apply_perspective(self,image):

        width, height = image.size
        image = np.array(image)

        # Dönüşüm için 4 nokta belirle (üst noktalar daha içeride olacak)
        src_pts = np.float32([
            [0, 0], [width, 0], [0, height], [width, height]
        ])
        dst_pts = np.float32([
            [width * 0.2, height * 0.1], [width * 0.8, height * 0.1], 
            [0, height], [width, height]
        ])

        # Perspektif dönüşüm matrisi
        matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
        warped = cv2.warpPerspective(image, matrix, (width, height))

        return Image.fromarray(warped)

    

    def random_place(self, image, canvas, random_placed_images):
        """Resmi ortak tuvale çakışma olmadan yerleştirir ve sadece şeffaf olmayan alanlar için bbox hesaplar."""
        repeat = True
        image = image.convert("RGBA")  # Şeffaflık desteklesin
        new_width, new_height = canvas.size
        bbox_data = []  # Bbox verilerini saklayacağımız liste

        # 📌 Şeffaf olmayan pikselleri tespit etmek için alpha kanalını al
        alpha_channel = np.array(image.split()[3])  # Alpha kanalı (0: Şeffaf, 255: Opak)
        
        # 📌 Opak piksellerin bulunduğu alanları belirle
        opak_pikseller = np.argwhere(alpha_channel > 0)  # Şeffaf olmayan piksellerin koordinatları

        if opak_pikseller.size == 0:
            print("❌ Tüm görüntü şeffaf, bbox hesaplanmadı.")
            return random_placed_images, canvas, bbox_data  # Hiç ekleme yapmadan geri dön

        # 📌 Bounding Box sınırlarını belirle (en küçük ve en büyük x, y değerleri)
        min_y, min_x = opak_pikseller.min(axis=0)  # Opak piksellerin en sol üst noktası
        max_y, max_x = opak_pikseller.max(axis=0)  # Opak piksellerin en sağ alt noktası

        # 📌 Şeffaf olmayan alanlara göre gerçek bounding box boyutları
        bbox_width = max_x - min_x
        bbox_height = max_y - min_y
        max_attempts = 100  # Yerleştirme denemesi sayısı
        attempts = 0
       
        x_shift = random.randint(0, new_width - bbox_width)
        y_shift = random.randint(0, new_height - bbox_height)

        

        cropped_image = image.crop((min_x, min_y, max_x, max_y))  # Şeffaf olmayan alanı kes
        canvas.paste(cropped_image, (x_shift, y_shift), cropped_image)

        # 📌 Listeye konumuyla birlikte ekle
        random_placed_images.append((x_shift, y_shift, cropped_image))

        # 📌 Bounding Box verisini kaydet (şeffaf olmayan alan için)
        x1, y1 = x_shift, y_shift
        x2, y2 = x_shift + bbox_width, y_shift + bbox_height
        bbox_data.append((x1, y1, x2, y2))  # (sol üst x, sol üst y, sağ alt x, sağ alt y)
        print("✅ Resim yerleştirildi!")

                
           
        return random_placed_images, canvas, bbox_data



    def bbox_plotting(self, canvas, bbox_list, i):
        """
        Tüm nesneler için verilen bbox_list içindeki bounding box'ları canvas üzerine çizer.
        """
        draw = ImageDraw.Draw(canvas)  # Canvas üzerine çizim yapmak için ImageDraw objesi oluştur

        for (x1, y1, x2, y2) in bbox_list:
            draw.rectangle([x1, y1, x2, y2], outline="red", width=3)  # Kırmızı çerçeve çiz
            draw.text((x1, y1 - 10), f"Object {i}", fill="red")  # Nesnenin adını yaz (isteğe bağlı)

        return canvas  # Bounding Box çizilmiş canvas'ı döndür


   






class COCOExporter:
    def __init__(self, output_file="annotations.json"):
        self.output_file = output_file
        self.data = {
            "images": [],
            "annotations": [],
            "categories": [{"id": 0, "name": "Person", "super_category": "object"},
                           {"id": 1, "name": "Sarı_Duba", "super_category": "object"},
                           {"id": 2, "name": "Yeşil_Duba", "super_category": "object"},
                           {"id": 3, "name": "Turuncu_Duba", "super_category": "object"},
                           {"id": 4, "name": "Siyah_Duba", "super_category": "object"},
                           {"id": 5, "name": "Kırmızı_Duba", "super_category": "object"},
                           {"id": 6, "name": "Düşman_İda", "super_category": "object"},
                           {"id": 7, "name": "Danger_Mark", "super_category": "object"},
                           {"id": 8, "name": "Boat", "super_category": "object"}
                           ]
        }
        
        self.category_map = {
    "Person": 0, "Sarı_Duba": 1, "Yeşil_Duba": 2, "Turuncu_Duba": 3, "Siyah_Duba": 4,
    "Kırmızı_Duba": 5, "Düşman_İda": 6, "Danger_Mark": 7, "Boat": 8 }
        self.image_id = 0
        self.annotation_id = 0  # Her annotation için ID sayacı

    def add_image(self, width, height):
        """
        Yeni bir resmi JSON dosyasına ekler ve image_id döndürür.
        """
        file_name = f"{self.image_id:06d}.png"  # 000001.png formatında dosya adı

        image_data = {
            "id": int(self.image_id),  # NumPy int64 hatasına karşı int() dönüştürüldü
            "file_name": file_name,
            "width": int(width),
            "height": int(height)
        }
        self.data["images"].append(image_data)
        
        current_image_id = self.image_id  # Mevcut image_id'yi sakla
        self.image_id += 1  # Bir sonraki resim için ID artır
        return current_image_id

    def add_annotation(self, image_id, bbox_list,category_id):
        """
        Her resme ait Bounding Box (BBox) verisini JSON’a ekler.
        COCO formatı: bbox = [x_min, y_min, width, height]
        """
        for bbox in bbox_list:
            x_min, y_min, x_max, y_max = bbox  # (x1, y1, x2, y2)
            width = x_max - x_min
            height = y_max - y_min
            area = width * height  # BBox alanı hesaplandı
            
            annotation_data = {
                "id": int(self.annotation_id),
                "image_id": int(image_id),
                "category_id": category_id,
                "bbox": [int(x_min), int(y_min), int(width), int(height)],
                "area": int(area),
                "iscrowd": 0
            }
            self.data["annotations"].append(annotation_data)
            self.annotation_id += 1  # Annotation ID'yi artır

    def get_category_id_from_filename(self, file_path):
        """Dosya isminden harfleri alır ve kategori ID belirler"""
        file_name = Path(file_path).stem  # 'Plane52' (uzantısız dosya adı)
        match = re.match(r"([a-zA-Z]+)", file_name)  # Sadece harfleri al

        if match:
            category_name = match.group(1)  # Örn: 'Plane'
        else:
            category_name = "none"  # Varsayılan isim

        # Kategori ID eşleşmesi
        return category_name, self.category_map.get(category_name, 1) 
    
    def save_json(self):
        """
        JSON dosyasını kaydeder.
        """
        with open(self.output_file, "w") as json_file:
            json.dump(self.data, json_file, indent=4)
        print(f"✅ COCO formatında annotations.json kaydedildi: {self.output_file}")


if __name__ == "__main__":


    # 📌 config.py'nin bulunduğu dizini sys.path'e ekle
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(current_dir)

    print(f"✅ sys.path güncellendi, yeni yollar: {sys.path}")

    # 📌 config.py dosyasını içe aktarmayı dene
    try:
        import config

        print("✅ config.py başarıyla import edildi!")
    except ModuleNotFoundError as e:
        print(f"❌ Hata: {e}. config.py dosyasının dizinde olduğundan emin olun!")

    # 📌 Blender sınıfını ve config.cfg() fonksiyonunu kullanarak Generator'ı oluştur
    Generator = Main_Process(cfg=config.cfg())
    output_dir = Path(Generator.cfg.out_folder)
    coco = COCOExporter()
    os.makedirs(output_dir, exist_ok=True)
    number_of_renders = Generator.cfg.number_of_image_data_renders
    j = -1
    bg_path = Generator.cfg.bg_paths
    k = 0
    while j < number_of_renders:
        j += 1
        i = 0
        bg_image = Image.open(random.choice(bg_path))
        bg_image = bg_image.resize((640, 640))
        bg_height, bg_width = bg_image.size
        image_list = []
        random_placed_images = []
        repeat = True
        bg_color = Generator.cfg.bg_color
        max_obj = 5
        canvas = Image.new("RGBA", bg_image.size, (0, 0, 0, 0))  # Şeffaf arka plan

        # 📌 Belirtilen sayıda render al
        
    
        for image_path in Path(output_dir).glob("*.png"):  # Sadece PNG dosyaları
            image = Image.open(image_path)
            image_list = Generator.make_transparent_and_resize(image, image_list, bg_color)
        number_of_samples = random.randint(1, min(len(image_list)-1, max_obj))
        
        print("number of samples: ",number_of_samples)
        """!!!!!!!!"""
        for image in random.sample(image_list, number_of_samples):
            i += 1
            k+=1
            
            category_name, category_id = coco.get_category_id_from_filename(image.filename)
        
            height, width = image.size
            
            random_placed_images, canvas, bbox_list= Generator.random_place(image,canvas,random_placed_images)
            

            print(number_of_samples)

            
            coco.add_annotation(coco.image_id, bbox_list, category_id)
               
                
        coco.add_image(bg_width, bg_height)
                     
        

        bg_image.paste(canvas, (0, 0), canvas)
        output_folder = "final_images"

        # Klasör yoksa oluştur
        os.makedirs(output_folder, exist_ok=True)

        # Dosyayı kaydetme
        bg_image.save(os.path.join(output_folder, f"{str(j).zfill(6)}.png"))
        
    coco.save_json()
    print("number of annotations: ",k)

"""potantial issues:
-- number of samples fazla olduğunda döngüye girme kısmı engellenecek

    -- dosyadaki objelerin ve resimlerin isimleri düzenlenecek
    -- dosyadaki resimlerin okunması düzenlenecek
    -- oluşturulan resimler ve objelerin isimleri düzenlenip dosyanın içine atılacak
    -- ayrıca bir show annotations dosyası oluşturulacak
    -- show annotations dosyası ile json dosyası okunacak
    -- json dosyası okunurken bounding boxlar çizilecek


yapıldı:

-- config dosyasına kategoriler yazılacak    
-- kategoriler ve super kategorilerin belirlenmesi
"""
