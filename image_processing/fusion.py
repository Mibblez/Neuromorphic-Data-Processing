import argparse
import numpy as np
import cv2

import mean_shift_segmentation
import otsu
import local_entropy

path_arg: str
blur_amount_arg: int = 11
otsu_min_threshold_arg: int = 125


def get_args():
    global path_arg, blur_amount_arg, otsu_min_threshold_arg
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path",
                        help='Directory containing images to be processed or a path to an image to be processed', type=str)

    args = parser.parse_args()

    path_arg = args.image_path


if __name__ == '__main__':
    otsu_threshold: int = 255
    mss_threshold: int = 100
    entropy_threshold: float = 0.7

    path_arg = "image_processing/whel.png"
    result_canvas = cv2.imread(path_arg)
    original_image = cv2.imread(path_arg)

    otsu_image = otsu.otsu_and_blur(result_canvas, blur_amount_arg, otsu_min_threshold_arg)
    mms_image = mean_shift_segmentation.mss(result_canvas, False, 5)
    entropy_image = local_entropy.get_entropy_image(result_canvas)

    for (i, row) in enumerate(result_canvas):
        for (j, pix) in enumerate(row):
            if(otsu_image[i][j] == otsu_threshold and mms_image[i][j][0] > mss_threshold and entropy_image[i][j] > entropy_threshold):
                result_canvas[i][j] = np.array([255, 255, 255])
            else:
                result_canvas[i][j] = np.array([0, 0, 0])

    cv2.imshow('Original', original_image)
    cv2.imshow('MSS', mms_image)
    cv2.imshow('Otsu', otsu_image)
    cv2.imshow('Entropy Image', entropy_image)
    cv2.imshow('Result', result_canvas)
    cv2.waitKey(0)
