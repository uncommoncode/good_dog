# Goal: This script is used to inspect the image size so we can figure out the best size to normalize at
#       This can also be used to calculate the amount of images with mapfile
# TODO: Make this script so that I can customize the resolution
# Result: I have decided using this script to settle on a resolution of 256x256
#         Verified that map file and original image have the same resolution

# This only takes images with a mask file - with labeled data

from PIL import Image
import os

def get_num_pixels(file_path):
  width, height = Image.open(file_path).size
  return (width, height)

def analyze_directory(directory_path):
  directory = os.fsencode(directory_path)
  count = 0
  for file in os.listdir(directory):
    file_name = os.fsdecode(file)
    if file_name.endswith(".jpg"):
      file_name_wo_extension = os.path.splitext(file_name)[0] 
      map_name = file_name_wo_extension + ".mask.0.png"

      map_path = os.path.join(directory_path,  map_name)
      file_path = os.path.join(directory_path, file_name)
      if os.path.exists(map_path):
        count = count + 1
        print(file_name + " : " + map_name)
        file_w, file_h = get_num_pixels(file_path)
        if width < 256 or height < 256:
          print("     Error: size invalid; please remove")
        # map_file_w, map_file_h = get_num_pixels(map_path)
        print("file width: " + str(file_w) + "; file height: " + str(file_h))
        # print("map_file width: " + str(map_file_w) + "; map_file height: " + str(map_file_h))
  print("total count: " + str(count))

directory_path = os.path.join(os.path.dirname(os.getcwd()), "Pictures", "cat+face")
print(directory_path)

analyze_directory(directory_path)

