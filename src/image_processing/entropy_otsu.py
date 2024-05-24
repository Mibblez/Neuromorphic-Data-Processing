""" OTSU THRESHOLDING DVS128 IMAGES """

import sys
import cv2
import numpy as np
import os
import argparse
from plotting_utils.plotting_helper import int_arg_positive_nonzero, path_arg, file_arg_image, int_arg_not_negative
from PIL import Image

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("image_file", help="Image to be processed", type=file_arg_image)
    parser.add_argument(
        "--blur_amount",
        "-b",
        help="The amount the image will be gaussian blurred (Must be an odd number)",
        type=int_arg_not_negative,
        required=True,
    )
    parser.add_argument(
        "--otsu_threshold",
        "-t",
        help="The minimum threshold for the otsu algorithm",
        default=125,
        type=int_arg_positive_nonzero,
    )
    parser.add_argument("--save_directory", "-d", help="Save file to directory", type=path_arg, default=".")

    args = parser.parse_args()

    if (args.blur_amount % 2) == 0:
        parser.error("Error: arg '--blur_amount' must be odd.")

    if args.otsu_threshold > 255:
        sys.exit("Error: arg '--otsu_threshold' must be between 0 and 255")

    return args


def otsu_and_blur(img: np.ndarray, blur_amount: int, otsu_min_threshold: int) -> np.ndarray:
    # Convert image to grayscale
    img_bw = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # apply guassian blur on src image
    img_blur = cv2.GaussianBlur(img_bw, (blur_amount, blur_amount), cv2.BORDER_DEFAULT)

    # applying Otsu thresholding as an extra flag in binary thresholding
    _, threshold_image = cv2.threshold(img_blur, otsu_min_threshold, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return threshold_image

# Entropy

# Convert an rgb image to a grayscale image
def rgb2gray(rgb: np.ndarray) -> np.ndarray:
    return np.dot(rgb[..., :3], [255 * 0.2989, 255 * 0.5870, 255 * 0.1140])


# Calculate entropy. Returns the entropy of a signal - signal must be a 1-D numpy array
def entropy(signal: np.ndarray) -> np.float64:
    lensig = signal.size
    symset = list(set(signal))
    propab = [np.size(signal[signal == i]) / (1.0 * lensig) for i in symset]
    ent = np.sum([p * np.log2(1.0 / p) for p in propab])
    return ent


def get_entropy_image(img: np.ndarray, convert_to_gray=True) -> np.ndarray:
    #if convert_to_gray:
    #    img = rgb2gray(img)

    N = 5
    S = img.shape
    E = np.array(img)

    for row in range(S[0]):
        for col in range(S[1]):
            Lx = np.max([0, col - N])
            Ux = np.min([S[1], col + N])
            Ly = np.max([0, row - N])
            Uy = np.min([S[0], row + N])
            region = img[Ly:Uy, Lx:Ux].flatten()
            E[row, col] = entropy(region)

    return E

def main(args: argparse.Namespace):
    # Grab filename from path
    file_name = os.path.basename(os.path.normpath(args.image_file))
    file_name = os.path.splitext(file_name)[0]

    # Image must read in as RGB and manually converted to grayscale with rgb2gray
    image = np.array(Image.open(args.image_file).convert("RGB"))

    entropy_image = get_entropy_image(image)

    otsu_image = otsu_and_blur(entropy_image, args.blur_amount, args.otsu_threshold)  

    cv2.imwrite(
        os.path.join(
            args.save_directory,
            f"{file_name}-entropy+otsu_threshold-{args.blur_amount}blur-{args.otsu_threshold}threshold.png",
        ),
        otsu_image,
    )


if __name__ == "__main__":
    args = get_args()
    main(args)
