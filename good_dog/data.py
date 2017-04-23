import glob
import os
import scipy.ndimage
import random
import shutil

def load_np_image(image_path):
    return scipy.ndimage.imread(image_path)

class DogsVsCats(object):
    def __init__(self, train_dir, test_dir=None):
        self.train_dir = train_dir
        self.test_dir = test_dir
        self.classes = ["cats", "dogs"]

    def train_iter(self, shuffle):
        """Return an iterator that yields pairs of (img_path, label)."""
        paths = glob.glob(os.path.join(self.train_dir, "*.jpg"))
        if shuffle:
            random.shuffle(paths)
        for path in paths:
            label = os.path.basename(path).partition(".")[0]
            yield (path, label)

    # TODO yield labels as well? Not sure where labels are...
    #def test_iter(self):
    #    """Return an iterator that yields unlabeled images."""
    #    pass

def load_training_test_sample(data_iterator, sample_size=None, test_pct=0.2):
    training_labels = []
    training_images = []
    test_images = []
    test_labels = []
    if sample_size is None:
        data = list(data_iterator)
        sample_size = len(data)
        data_iterator = iter(data)
    test_size = int(sample_size * test_pct)
    training_size = sample_size - test_size
    for i in range(training_size):
        image_path, label = data_iterator.next()
        training_images.append(image_path)
        training_labels.append(label)
    for i in range(test_size):
        image_path, label = data_iterator.next()
        test_images.append(image_path)
        test_labels.append(label)
    return training_images, training_labels, test_images, test_labels

def require_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def copy_to_directory(source_path, target_dir):
    shutil.copy(source_path, target_dir)

def make_keras_training(data_iterator, out_dir, sample_size=None, validation_pct=0.2):
    samples = load_training_test_sample(data_iterator, sample_size, validation_pct)
    training_images, training_labels, validation_images, validation_labels = samples
    for image_path, label in zip(training_images, training_labels):
        image_dir = os.path.join(out_dir, "train", label)
        require_directory(image_dir)
        copy_to_directory(image_path, image_dir)
    for image_path, label in zip(validation_images, validation_labels):
        image_dir = os.path.join(out_dir, "validate", label)
        require_directory(image_dir)
        copy_to_directory(image_path, image_dir)
