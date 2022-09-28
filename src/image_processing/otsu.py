""" OTSU THRESHOLDING DVS128 IMAGES """

import sys
import cv2
import numpy as np
import os
import argparse

path_arg: str = ""
blur_amount_arg: int = 0
otsu_min_threshold_arg: int = 125


def get_args():
    global path_arg, blur_amount_arg, otsu_min_threshold_arg

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "image_path", help="Directory containing images to be processed or a path to an image to be processed", type=str
    )
    parser.add_argument(
        "--blur_amount",
        "-b",
        help="The amount the image will be gaussian blurred. (Must be an odd number) ",
        type=int,
        required=True,
    )
    parser.add_argument("--otsu_threshold", "-t", help="The minimum threshold for the otsu algorithm.", type=int)

    args = parser.parse_args()

    # Check if image path exists and is an image file type
    if os.path.exists(args.image_path):
        if not os.path.splitext(args.image_path)[1] in [".png", ".jpeg", ".jpg"]:
            sys.exit(f"ERROR: '{args.image_path}' is not an image.")
        else:
            path_arg = args.image_path
    else:
        sys.exit(f"ERROR: '{args.image_path}' does not exist")

    blur_amount_arg = args.blur_amount
    if (blur_amount_arg % 2) == 0:
        sys.exit("Error: arg '--blur_amount' must be odd.")
    elif blur_amount_arg <= 0:
        sys.exit("Error: arg '--blur_amount' cannot be less than zero")

    if args.otsu_min_threshold is not None:
        otsu_min_threshold_arg = args.otsu_threshold

    if (otsu_min_threshold_arg < 0) or (otsu_min_threshold_arg > 255):
        sys.exit("Error: arg '--otsu_threshold' must be between 0 and 255")


def otsu_and_blur(img: np.ndarray, blur_amount: int, otsu_min_threshold: int) -> np.ndarray:
    # Convert image to grayscale
    img_bw = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # apply guassian blur on src image
    img_blur = cv2.GaussianBlur(img_bw, (blur_amount, blur_amount), cv2.BORDER_DEFAULT)

    # applying Otsu thresholding as an extra flag in binary thresholding
    ret, threshold_image = cv2.threshold(img_blur, otsu_min_threshold, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return threshold_image


if __name__ == "__main__":
    get_args()

    normal_image = cv2.imread(path_arg)

    otsu_image = otsu_and_blur(normal_image, blur_amount_arg, otsu_min_threshold_arg)

    # Grab filename from path
    file_name = os.path.basename(os.path.normpath(path_arg))
    file_name = os.path.splitext(file_name)[0]

    cv2.imwrite(f"{file_name}_blur.png", otsu_image)
