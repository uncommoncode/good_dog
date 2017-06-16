# Goal: This script is used to pad the images into squares with black pixels
#       This also normalizes the mask image into 0 and 1s, instead of colors
#       And this saves the images and their corresponding mask files into another directory: output_dir
# Requirements: Directory needs to be clean - just with qualifying jpgs with their corresponding mapfiles
#               i.e., Image: _image_.jpg --> Mask file: _image_.mask.0.png

from PIL import Image
import os
import argparse
import random
import numpy as np

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
  count = 0
  for file_name in os.listdir(directory_path):
    if file_name.endswith(".jpg"):
      file_path = os.path.join(directory_path, file_name)
      file_name_wo_extension = os.path.splitext(file_name)[0]
      map_name = file_name_wo_extension + ".mask.0.png"
      map_file_path = os.path.join(directory_path, map_name)
      if os.path.exists(map_file_path):
        count = count + 1
        print("Padding image and map: " + file_name_wo_extension)
        img = Image.open(file_path)
        msk = Image.open(map_file_path)
        size = (max(img.size), max(img.size))
        # pad original image
        new_im = pad_image(size, new_size, img)
        save_img(new_im, file_name, output_path)

	# pad original mask
        new_msk = pad_image(size, new_size, msk, 0)
        msk = binarize_image(new_msk, new_msk.size, map_file_path)
        save_img(msk, map_name, output_path)

  print("There are " + str(count) + " images")

def get_white_noise_image(width, height):
  pil_map = Image.new("RGB", (width, height))
  random_grid = map(lambda x: (int(random.random() * 256), int(random.random() * 256), int(random.random() * 256)), [0] * width * height)
  pil_map.putdata(list(random_grid), scale=1, offset=0)
  return pil_map
    
def pad_image(size, new_size, img, with_white_noise=True):
  new_im = Image.new("RGB", size)
  new_im.paste(img, (0, 0))
  if with_white_noise:
    n_width = size[0]-img.size[0] if size[0] > img.size[0] else img.size[0]
    n_height = size[1]-img.size[1] if size[1] > img.size[1] else img.size[1]
    anchor_x = img.size[0] if size[0] > img.size[0] else 0
    anchor_y = img.size[1] if size[1] > img.size[1] else 0
    new_im.paste(get_white_noise_image(n_width, n_height), (anchor_x, anchor_y))

  new_im = new_im.resize((new_size, new_size), Image.BICUBIC)
  return new_im

def save_img(img, file_name, output_path):
  file_name = os.path.splitext(file_name)[0] + "_new.jpg"
  file_path = os.path.join(output_path, file_name)

  print("Saving: " + file_name)
  try:
    img.save(file_path)
  except IOError:
    print("Error: cannot save for" + file_path)

def binarize_image(image_file, target_path, threshold):
    """Binarize an image."""
    image = image_file.convert('RGB')  # convert image to monochrome
    image = np.array(image)
    image = binarize_array(image, 0)
    img = Image.fromarray(image, 'RGB')
    img = img.convert('L')
    # img.show()
    return img

def binarize_array(numpy_array, threshold=200):
  for i in range(len(numpy_array)):
    for j in range(len(numpy_array[0])):
      if numpy_array[i][j][0] > 0 or numpy_array[i][j][1] > 0:
        numpy_array[i][j] = (255, 255, 255)
      else:
        numpy_array[i][j] = (0, 0, 0)
  return numpy_array
  
def main():
  args = get_arguments()
  pad_images_from_directory(args.input_dir, args.output_dir, args.size)

if __name__ == '__main__':
  main()
