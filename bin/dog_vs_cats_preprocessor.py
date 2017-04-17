import good_dog.data

def dog_vs_cats_to_keras(train_dir, output_dir, sample_size, validation_pct):
    dog_vs_cats = good_dog.data.DogsVsCats(train_dir)
    good_dog.data.make_keras_training(dog_vs_cats.train_iter(shuffle=True), out_dir=output_dir, sample_size=sample_size,
                                      validation_pct=validation_pct)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_dir", required=True)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--sample_size", default=None)
    parser.add_argument("--validation_pct", default=0.2)
    args = parser.parse_args()
    dog_vs_cats_to_keras(train_dir=args.train_dir, output_dir=args.output_dir, sample_size=args.sample_size,
                         validation_pct=args.validation_pct)
