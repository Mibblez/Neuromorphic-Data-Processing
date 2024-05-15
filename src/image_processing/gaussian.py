""" GAUSSIAN IMAGE DVS128 IMAGES """


import cv2
import numpy as np
import os
import argparse
from plotting_utils.plotting_helper import int_arg_positive_nonzero, path_arg, file_arg_image, int_arg_not_negative


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
        "--blur_iterations",
        "-i",
        help="The number of times the image will be blurred",
        type=int_arg_positive_nonzero,
        default=1,
    )
    parser.add_argument("--save_directory", "-d", help="Save file to directory", type=path_arg, default=".")

    args = parser.parse_args()

    if (args.blur_amount % 2) == 0:
        parser.error("Error: arg '--blur_amount' must be odd.")

    return args


def gaussian_blur(img: np.ndarray, blur_amount: int, blur_iterations: int) -> np.ndarray:
    # Convert image to grayscale
    img_bw = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # apply guassian blur on src image
    blur_result = img_bw
    for _ in range(blur_iterations):
        blur_result = cv2.GaussianBlur(blur_result, (blur_amount, blur_amount), cv2.BORDER_DEFAULT)

    return blur_result


def main(args: argparse.Namespace):
    normal_image = cv2.imread(args.image_file)

    gaussian_image = gaussian_blur(normal_image, args.blur_amount, args.blur_iterations)

    # Grab filename from path
    file_name = os.path.basename(os.path.normpath(args.image_file))
    file_name = os.path.splitext(file_name)[0]

    cv2.imwrite(
        os.path.join(
            args.save_directory,
            f"{file_name}-{args.blur_amount}-blur-{args.blur_iterations}-iterations.png",
        ),
        gaussian_image,
    )


if __name__ == "__main__":
    args = get_args()
    main(args)
