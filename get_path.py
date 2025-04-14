import os


def get_file_paths(directory):
    i=0
    file_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            
            file_paths.append(os.path.join(root, file))
            i+=1
            if i>8:
                break
    return file_paths
    


def get_obj_file_paths(directory):
    i=0
    obj_file_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.obj'):
                obj_file_paths.append(os.path.join(root, file))
                i+=1
                if i>8:
                    break
    return obj_file_paths
