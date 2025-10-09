import os 
import math 
 
def get_size(path: str) -> int:
    """ Возвращает размер директории в байтах """
    total_size = 0 
    for dirpath, dirnames, filenames in os.walk(path): 
        for f in filenames: 
            fp = os.path.join(dirpath, f) 
            total_size += os.path.getsize(fp) 
    return total_size 
 
def convert_size(size_bytes): 
   if size_bytes == 0: 
       return "0B" 
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB") 
   i = int(math.floor(math.log(size_bytes, 1024))) 
   p = math.pow(1024, i) 
   s = round(size_bytes / p, 2) 
   return "%s %s" % (s, size_name[i]) 
folder_size = get_size(r"C:\Users\Semen\Desktop\Programming\ReSave Manager")
print(folder_size)
print(convert_size(folder_size)) 
