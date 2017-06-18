# Goal: This script is used to read from the train/test directory to generate the csv file so that notebook can read it quickly
import os
import csv

def consolidate_file_from_directory(directory, o_dir):
  with open(o_dir, 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    count = 0
    for file_name in os.listdir(directory):
      row = []
      if file_name.endswith(".jpg"):
        file_path = os.path.join(directory, file_name)
        file_name_wo_extension = os.path.splitext(file_name)[0]
        file_name_deconstructed = file_name_wo_extension.split('_')
        if len(file_name_deconstructed) == 3:
          map_name = file_name_deconstructed[0] + "_" + file_name_deconstructed[1] + ".mask.0_new.jpg"
        elif "cat" in file_name_wo_extension:
          map_name = file_name_deconstructed[0] + ".mask.0_new.jpg"
        else:
          continue
        map_file_path = os.path.join(directory, map_name)
        if os.path.exists(map_file_path):
          row.append(file_path)
          row.append(map_file_path)
          count = count + 1
      writer.writerow(row)
    print("Total image count: ", str(count))

# consolidate_file_from_directory(os.path.join(os.path.dirname(os.getcwd()), "Pictures", "train"), os.path.join(os.path.dirname(os.getcwd()), "Pictures", "train.csv"))
consolidate_file_from_directory(os.path.join(os.path.dirname(os.getcwd()), "Pictures", "test"), os.path.join(os.path.dirname(os.getcwd()), "Pictures","test.csv"))

