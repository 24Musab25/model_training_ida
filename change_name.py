import os

# Ana dizini belirtin
base_dir = 'objects'

# Her klasörü dolaş
for folder in os.listdir(base_dir):
    if folder.endswith('_transparent'):
        # Yeni klasör adını oluştur
        new_folder_name = folder.replace('_transparent', '')
        old_folder_path = os.path.join(base_dir, folder)
        new_folder_path = os.path.join(base_dir, new_folder_name)

        # Klasörü yeniden adlandır
        os.rename(old_folder_path, new_folder_path)
    else:
        new_folder_name = folder
        new_folder_path = os.path.join(base_dir, new_folder_name)
        # Dosyaları yeniden adlandır
    counter = 1
    for file in os.listdir(new_folder_path):
        if file.endswith('.glb'):
            old_file_path = os.path.join(new_folder_path, file)
            new_file_name = f'{new_folder_name}{counter}.glb'
            new_file_path = os.path.join(new_folder_path, new_file_name)

            os.rename(old_file_path, new_file_path)
            counter += 1
