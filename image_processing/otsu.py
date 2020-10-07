""" OTSU THRESHOLDING DVS128 IMAGES """

import sys
import cv2
import argparse

arg_path: str = ''
blur_amount: int = 0
otsu_min_threshold: int = 125


def get_args():
    global arg_path, blur_amount, otsu_min_threshold

    parser = argparse.ArgumentParser()
    parser.add_argument("image_path",
                        help='Directory containing images to be processed or a path to an image to be processed', type=str)
    parser.add_argument("--blur_amount", "-b",
                        help='The amount the image will be gaussian blurred. (Must be an odd number) ', type=int, required=True)
    parser.add_argument("--otsu_threshold",
                        "-t", help='The minimum threshold for the otsu algorithm.', type=int)

    args = parser.parse_args()

    blur_amount = args.blur_amount
    if (blur_amount % 2) == 0:
        sys.exit("Error: arg '--blur_amount' must be odd.")
    elif blur_amount <= 0:
        sys.exit("Error: arg '--blur_amount' cannot be less than zero")

    if otsu_min_threshold is not None:
        otsu_min_threshold = args.otsu_threshold
    elif (otsu_min_threshold < 0) or (otsu_min_threshold > 255):
        sys.exit("Error: arg '--otsu_threshold' must be between 0 and 255")

    arg_path = args.image_path


if __name__ == '__main__':
    get_args()

    # Read image and convert to grayscale
    img = cv2.imread(arg_path)
    img_bw = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # apply guassian blur on src image
    img_blur = cv2.GaussianBlur(img_bw, (blur_amount, blur_amount), cv2.BORDER_DEFAULT)

    # applying Otsu thresholding as an extra flag in binary thresholding
    ret, threshold_image = cv2.threshold(img_blur, otsu_min_threshold, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    cv2.imwrite("output_otsu_blur.png", threshold_image)
