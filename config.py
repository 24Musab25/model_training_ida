import get_path

directory_obj = "./objects/"
directory_glb = "./objects_glb/"
directory_bg = "./bg/"
directory_textures = "./textures/"
directory_ss = "./screenshots/"

class cfg:
    def __init__(self):
        self.file_name = "Screenshot"
        self.out_folder = "Screenshots"
        self.bg_paths = get_path.get_file_paths(directory_bg)
        self.object_folders = get_path.get_obj_file_paths(directory_obj)
        self.object_folders_glb = get_path.get_file_paths(directory_glb)
        self.texture_folders = get_path.get_file_paths(directory_textures)
        self.bg_color = (60,60,60)
        self.number_of_object_renders = 20
        self.number_of_image_data_renders = 20
        

        
