# Goal: This script is used to pad the images into squares with black pixels
#       And this saves the images and their corresponding mask files into another directory: output_dir
# Requirements: Directory needs to be clean - just with qualifying jpgs with their corresponding mapfiles
#               i.e., Image: _image_.jpg --> Mask file: _image_.mask.0.png


from PIL import Image
import os

output_dir = os.path.join(os.path.dirname(os.getcwd()), "Pictures", "output")
if not os.path.exists(output_dir):
  os.makedirs(output_dir)

def pad_images_from_directory(directory_path):
  directory = os.fsencode(directory_path)
  for file in os.listdir(directory):
    file_name = os.fsdecode(file)
    if file_name.endswith(".jpg"):
      file_path = os.path.join(directory_path, file_name)
      file_name_wo_extension = os.path.splitext(file_name)[0]
      map_name = file_name_wo_extension + ".mask.0.png"
      map_file_path = os.path.join(directory_path, map_name)
      if os.path.exists(map_file_path):
        print("Padding image and map: " + file_name_wo_extension)
        img = Image.open(file_path)
        msk = Image.open(map_file_path)
        fw, fh = img.size 
        pad_image(fw, fh, img, file_name, directory_path)
        pad_image(fw, fh, msk, map_name, directory_path)
    
def pad_image(fw, fh, img, filename, directory_path):
  new_size = (max(fw, fh), max(fw, fh))
  new_im = Image.new("RGB", new_size)
  new_im.paste(img, (0, 0))
  newfilename = os.path.splitext(filename)[0] + "_new.jpg"
  newfilepath = os.path.join(output_dir, newfilename)
  print("Saving: " + newfilename)
  try:
    new_im.save(newfilepath)
  except IOError:
    print("Error: cannot save for" + newfilepath)
  
  
directory_path = os.path.join(os.path.dirname(os.getcwd()), "Pictures", "cat+face")
print(directory_path)

pad_images_from_directory(directory_path)
