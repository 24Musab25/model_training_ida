import bpy
import os
import random
from PIL import Image
import sys
from pathlib import Path
import math

class Blender:
    def __init__(self, cfg):
        self.cfg = cfg
        self.bbox_list = []

    def save_ss(self, i):
        print("save_ss started")
        # 📌 Dosya yollarını belirle
        y = random.randint(0, len(self.cfg.texture_folders) - 1)
        z = random.randint(0, len(self.cfg.object_folders_glb) - 1)

        print("random indexler atandı")
        obj_file_glb = self.cfg.object_folders_glb[z]
        texture_folder = self.cfg.texture_folders[y]
        filename = self.cfg.file_name

        file_name = os.path.basename(obj_file_glb)  # 'Plane.glb'
        category_name, _ = os.path.splitext(file_name)  # ('Plane', '.glb')

        # 1️⃣ Sahneyi temizle
        print("sahne temizleniyor")
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        print("sahne temizlendi")

        


        # 2️⃣ GLB Dosyasını İçe Aktar
        print("GLB obje aktarılıyor...")
        bpy.ops.import_scene.gltf(filepath=obj_file_glb)  # ✅ GLB için değiştirildi!
        print("GLB obje aktarıldı!")


        # 📌 Sahnedeki tüm nesneleri yazdır
        print("📌 Sahnedeki tüm nesneler:")
        for obj in bpy.context.scene.objects:
            print(f"- {obj.name} ({obj.type})")

        # 📌 SADECE MESH NESNELERİNİ SEÇ!
        mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']

        if mesh_objects:
            obj = mesh_objects[0]  # İlk mesh nesnesini seç
            print(f"✅ Seçilen MESH obje: {obj.name}")
        else:
            print("❌ Hata: GLB içe aktarıldı ama MESH nesnesi bulunamadı!")
            obj = None


        

        # 3️⃣ Objeyi Aktif Hale Getir
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        # 4️⃣ Materyal ve Doku Kontrolü
        if obj.data and obj.data.materials and len(obj.data.materials) > 0:
            print("✅ GLB kendi materyalini içeriyor, dokunulmuyor.")
            material = obj.data.materials[0]
        else:
            print("⚠️ Materyal yok, yeni materyal oluşturuluyor.")
            material = bpy.data.materials.new(name="TextureMaterial")
            material.use_nodes = True
            obj.data.materials.append(material)

            # 🎨 Shader node sistemi kur
            nodes = material.node_tree.nodes
            links = material.node_tree.links

            # Eski node'ları sil
            for node in nodes:
                nodes.remove(node)

            # Yeni node'lar oluştur
            bsdf_node = nodes.new(type="ShaderNodeBsdfPrincipled")
            bsdf_node.location = (0, 0)

            output_node = nodes.new(type="ShaderNodeOutputMaterial")
            output_node.location = (300, 0)

            links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])

            # 📌 Doku ekle (texture_folder'dan)
            if texture_folder:
                import glob
                texture_candidates = glob.glob(os.path.join(texture_folder, "*.png")) + glob.glob(os.path.join(texture_folder, "*.jpg"))
                if texture_candidates:
                    texture_path = random.choice(texture_candidates)
                    print(f"🖼️ Seçilen Doku: {texture_path}")

                    texture_node = nodes.new(type="ShaderNodeTexImage")
                    texture_node.location = (-300, 0)

                    try:
                        texture_node.image = bpy.data.images.load(texture_path)
                        links.new(bsdf_node.inputs["Base Color"], texture_node.outputs["Color"])
                        print("✅ Yeni doku başarıyla eklendi!")
                    except Exception as e:
                        print(f"❌ Doku yüklenemedi! Hata: {e}")
                else:
                    print("⚠️ Doku klasöründe .jpg veya .png dosyası bulunamadı.")


        # 6️⃣ UV Mapping Kontrolü
        if not obj.data.uv_layers or len(obj.data.uv_layers) == 0:
            print("⚠️ UV haritası eksik, oluşturuluyor...")
            obj.data.uv_layers.new(name="UVMap")
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.uv.smart_project(angle_limit=66)
                bpy.ops.object.mode_set(mode='OBJECT')
                print("✅ Smart UV Mapping uygulandı!")
            except RuntimeError:
                print("❌ Hata: Edit Mode'a geçilemedi. (Background modda çalışıyorsan normaldir.)")
        else:
            print("✅ UV Mapping zaten mevcut, yeniden uygulanmadı.")


        # 8️⃣ Objeyi Rastgele Döndür
        obj.rotation_euler = (
            random.uniform(0, 6.28),
            random.uniform(0, 6.28),
            random.uniform(0, 6.28)
        )

        # 9️⃣ Render Motorunu Ayarla (Cycles veya Eevee)
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.samples = 128
        bpy.context.scene.render.film_transparent = True
        bpy.context.scene.world.color = (0, 0, 0)



        # 1️⃣1️⃣ Kamera Ayarları
        scene = bpy.context.scene
        camera = scene.camera
        if camera is None:
            cam_data = bpy.data.cameras.new(name="Camera")
            cam_object = bpy.data.objects.new("Camera", cam_data)
            scene.collection.objects.link(cam_object)
            scene.camera = cam_object
            camera = cam_object

        # 2️⃣ Kamerayı rastgele bir konuma yerleştir
        x = random.uniform(-4, -2) if random.choice([True, False]) else random.uniform(2, 4)
        y = random.uniform(-4, -2) if random.choice([True, False]) else random.uniform(2, 4)
        z = random.uniform(-4, -2) if random.choice([True, False]) else random.uniform(2, 4)


        camera.location = (
            x,
            y,
            z
        )

        light_data = bpy.data.lights.new(name="Camera_Back_Light", type="POINT")
        light_data.energy = 2000  # Işık gücü
        light_object = bpy.data.objects.new(name="Camera_Back_Light", object_data=light_data)
        bpy.context.collection.objects.link(light_object)

        # Işığı kameranın biraz arkasına yerleştir
        light_offset = -1  # Kameranın arkasında belirli bir mesafe
        if camera.location.x == 0 or camera.location.y == 0 or camera.location.z == 0:
            light_object.location = (
                camera.location.x + light_offset,
                camera.location.y + light_offset,
                camera.location.z + light_offset)
        else:
            light_object.location = (
            camera.location.x + camera.location.x/abs(camera.location.x)* light_offset,
            camera.location.y + camera.location.y/abs(camera.location.y)* light_offset,  # Y ekseninde arkaya kaydır
            camera.location.z + camera.location.z/abs(camera.location.z)* light_offset  # Biraz yukarı kaldır
        )

        print(f"💡 Işık eklendi! Konum: {light_object.location}")
        print("✅ Sahneye 1 ışık eklendi ve kamera ayarlandı!")


        # 3️⃣ Eski "Track To" Constraint'leri temizle
        for constraint in camera.constraints:
            camera.constraints.remove(constraint)

        # 4️⃣ Yeni "Track To" Constraint ekle (Kamera objeye bakacak)
        track_constraint = camera.constraints.new(type='TRACK_TO')
        track_constraint.target = obj
        track_constraint.track_axis = 'TRACK_NEGATIVE_Z'  # Kameranın -Z ekseni objeye baksın
        track_constraint.up_axis = 'UP_Y'  # Y ekseni yukarı baksın

        # 5️⃣ Kamera Clipping Ayarları (Görüş mesafesi artırılıyor)
        bpy.data.cameras["Camera"].clip_start = 0.1
        bpy.data.cameras["Camera"].clip_end = 500

        # 1️⃣2️⃣ Render Ayarları
        screenshot_path = os.path.join(output_dir, category_name + str(i) + ".png")
        scene.render.filepath = screenshot_path
        scene.render.resolution_x = 1920
        scene.render.resolution_y = 1080
        scene.render.image_settings.file_format = 'PNG'

        # 1️⃣3️⃣ Render Al ve Kaydet
        bpy.ops.render.render(write_still=True)
        print(f"📸 Görüntü PNG olarak kaydedildi: {obj.name}")
        print(str(i) + "th png file")

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
    Generator = Blender(cfg=config.cfg())
    output_dir = Path(Generator.cfg.out_folder)
    os.makedirs(output_dir, exist_ok=True)
    number_of_renders = Generator.cfg.number_of_object_renders
    bg_path = Generator.cfg.bg_paths
    bg_image = Image.open(random.choice(bg_path))
    image_list = []
    repeat = True
    bg_color = Generator.cfg.bg_color


    # 📌 Belirtilen sayıda render al
    i = 0
    while i <= number_of_renders:
        i += 1
        Generator.save_ss(i)