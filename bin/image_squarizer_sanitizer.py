# Goal: This script is used to pad the images into squares with black pixels
#       This also normalizes the mask image into 0 and 1s, instead of colors
#       And this saves the images and their corresponding mask files into another directory: output_dir
# Requirements: Directory needs to be clean - just with qualifying jpgs with their corresponding mapfiles
#               i.e., Image: _image_.jpg --> Mask file: _image_.mask.0.png

from PIL import Image
import os
import argparse

OUTPUT = os.path.join(os.path.dirname(os.getcwd()), "Pictures", "output")
INPUT = os.path.join(os.path.dirname(os.getcwd()), "Pictures", "cat+face")

class readable_dir(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        prospective_dir = values
        if not os.path.isdir(prospective_dir):
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a valid path".format(prospective_dir))
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace, self.dest, prospective_dir)
        else:
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a readable dir".format(prospective_dir))

def get_arguments():
  parser = argparse.ArgumentParser(description="Sanize good dog cat dataset. :P")
  parser.add_argument('-i', '--input_dir', action=readable_dir, default=INPUT)
  parser.add_argument('-o', '--output_dir', action=readable_dir, default=OUTPUT)
  parser.add_argument('-s', '--size', type=int, default=256)
  return parser.parse_args()

def pad_images_from_directory(directory_path, output_path, new_size):
  for file_name in os.listdir(directory_path):
    if file_name.endswith(".jpg"):
      file_path = os.path.join(directory_path, file_name)
      file_name_wo_extension = os.path.splitext(file_name)[0]
      map_name = file_name_wo_extension + ".mask.0.png"
      map_file_path = os.path.join(directory_path, map_name)
      if os.path.exists(map_file_path):
        print("Padding image and map: " + file_name_wo_extension)
        img = Image.open(file_path)
        msk = Image.open(map_file_path)
        size = (max(img.size), max(img.size))
        pad_image(size, new_size, img, file_name, output_path)
        binarizeImage(msk, msk.size, map_file_path)
        pad_image(size, new_size, msk, map_name, output_path)
    
def pad_image(size, new_size, img, filename, directory_path):
  new_im = Image.new("RGB", size)
  new_im.paste(img, (0, 0))
  # Question: not sure if nearest is the best option here
  new_im = new_im.resize((new_size, new_size), Image.NEAREST)
  newfilename = os.path.splitext(filename)[0] + "_new.jpg"
  newfilepath = os.path.join(directory_path, newfilename)
  print("Saving: " + newfilename)
  try:
    new_im.save(newfilepath)
  except IOError:
    print("Error: cannot save for" + newfilepath)

def binarizeImage(img, size, img_path):
  pix = img.load()
  for x in range(size[0]):
    for y in range(size[1]):
      color = pix[x, y]
      break
      if 0 != color:
        pix[x, y] = 1
      else:
        pix[x, y] = 0
  # This below line NEEDS be commented OR deleted. Damn it learned it the hard way
  # img.show()
  img.save(img_path)
  
def main():
  args = get_arguments()
  pad_images_from_directory(args.input_dir, args.output_dir, args.size)

if __name__ == '__main__':
  main()
