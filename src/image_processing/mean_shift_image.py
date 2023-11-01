import argparse
import os
import numpy as np
from PIL import Image

from sklearn.cluster import MeanShift, estimate_bandwidth
from skimage.color.colorlabel import label2rgb

from plotting_utils.plotting_helper import path_arg, file_arg_image


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "image_file",
        help="Directory containing images to be processed or a path to an image to be processed",
        type=file_arg_image,
    )
    parser.add_argument("--subtract_image", "-s", help="Subtract mean shifted image from the original image", type=bool)
    parser.add_argument("--save_directory", "-d", help="Save file to directory", type=path_arg, default=".")
    parser.add_argument("--infinite_bandwidth", "-i", help="Infinite bandwidth", action="store_true")
    args = parser.parse_args()

    # TODO: Implement subtract_arg.
    # When set, subtract white pixels from original image and display the resulting image

    return args


def main(args: argparse.Namespace):
    original_image = np.array(Image.open(args.image_file).convert("RGB"))

    original_shape = original_image.shape
    flat_image = np.reshape(original_image, [-1, 3])

    bandwidth = estimate_bandwidth(flat_image, quantile=0.1, n_samples=100, n_jobs=4) if args.infinite_bandwidth else None

    mean_shift = MeanShift(bandwidth=bandwidth, bin_seeding=True)

    mean_shift.fit(flat_image)

    # (r,g,b) vectors corresponding to the different clusters after meanshift
    labels = mean_shift.labels_

    # Displaying segmented image
    segmented_image = np.reshape(labels, original_shape[:2])

    superpixels = label2rgb(segmented_image, original_image, kind="avg")

    result_image = Image.fromarray(superpixels)

    file_name = os.path.basename(os.path.normpath(args.image_file))  # Get file at end of path
    file_name = os.path.splitext(file_name)[0]  # Strip off file extension

    result_image.save(os.path.join(args.save_directory, f"{file_name}-mean_shift.png"))


if __name__ == "__main__":
    args = get_args()
    main(args)
