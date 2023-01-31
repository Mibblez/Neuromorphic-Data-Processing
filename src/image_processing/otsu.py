""" OTSU THRESHOLDING DVS128 IMAGES """

import sys
import cv2
import numpy as np
import os
import argparse
from plotting_utils.plotting_helper import int_arg_positive_nonzero, path_arg, file_arg, int_arg_not_negative


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("image_file", help="Image to be processed", type=file_arg)
    parser.add_argument(
        "--blur_amount",
        "-b",
        help="The amount the image will be gaussian blurred. (Must be an odd number)",
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

    if not os.path.splitext(args.image_file)[1] in (".png", ".jpeg", ".jpg"):
        parser.error(f"ERROR: '{args.image_file}' is not an image.")

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


def main(args: argparse.Namespace):
    normal_image = cv2.imread(args.image_file)

    otsu_image = otsu_and_blur(normal_image, args.blur_amount, args.otsu_threshold)

    # Grab filename from path
    file_name = os.path.basename(os.path.normpath(args.image_file))
    file_name = os.path.splitext(file_name)[0]

    cv2.imwrite(
        os.path.join(
            args.save_directory,
            f"{file_name}-otsu_threshold-{args.blur_amount}blur-{args.otsu_threshold}threshold.png",
        ),
        otsu_image,
    )


if __name__ == "__main__":
    args = get_args()
    main(args)
