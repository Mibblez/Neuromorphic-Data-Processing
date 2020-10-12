import argparse
import os
import sys
import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib

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
    parser.add_argument("--blur_amount", "-b",
                        help='The amount the image will be gaussian blurred. (Must be an odd number) ', type=int)
    parser.add_argument("--otsu_threshold", "-t",
                        help='The minimum threshold for the otsu algorithm.', type=int)

    args = parser.parse_args()

    # Check if image path exists and is an image file type
    if os.path.exists(args.image_path):
        if not os.path.splitext(args.image_path)[1] in ['.png', '.jpeg', '.jpg']:
            sys.exit(f"ERROR: '{args.image_path}' is not an image.")
        else:
            path_arg = args.image_path
    else:
        sys.exit(f"ERROR: '{args.image_path}' does not exist")

    # Ensure that the blur amount arg is valid
    if args.blur_amount is not None:
        blur_amount_arg = args.blur_amount
        if (blur_amount_arg % 2) == 0:
            sys.exit("Error: arg '--blur_amount' must be odd.")
        elif blur_amount_arg <= 0:
            sys.exit("Error: arg '--blur_amount' cannot be less than zero")

    if args.otsu_threshold is not None:
        if args.otsu_threshold <= 255 and args.otsu_threshold >= 0:
            otsu_min_threshold_arg = args.otsu_threshold
        else:
            sys.exit("ERROR: Otsu Threshold must be set between 255 and 0.")


def generate_fusion_plot(original: np.ndarray, result: np.ndarray, otsu: np.ndarray, mss: np.ndarray, entropy: np.ndarray):
    plot_title = os.path.basename(os.path.normpath(path_arg))
    plot_title = os.path.splitext(plot_title)[0]

    matplotlib.use("TkAgg")     # Use TkAgg rendering backend for matplotlib
    f, axes = plt.subplots(nrows=2, ncols=3, sharex=False, sharey=False)
    f.set_size_inches(10, 5)
    f.suptitle(plot_title, fontsize=16)

    plt.gray()      # Set default colormap to grayscale
    plt.tight_layout()

    axes[0, 0].imshow(original)
    axes[0, 0].set_title('Orignal')
    axes[0, 0].axis('off')

    axes[0, 1].imshow(result)
    axes[0, 1].set_title('Fusion Image')
    axes[0, 1].axis('off')

    axes[0, 2].remove()

    axes[1, 0].imshow(otsu)
    axes[1, 0].set_title('Gaussian Blur Otsu')
    axes[1, 0].axis('off')

    axes[1, 1].imshow(mss)
    axes[1, 1].set_title('Mean Shift')
    axes[1, 1].axis('off')

    axes[1, 2].imshow(entropy)
    axes[1, 2].set_title('Entropy')
    axes[1, 2].axis('off')

    if True:
        plt.savefig(f"{plot_title}_fusion.png")
        plt.close()
    else:
        plt.show()


if __name__ == '__main__':
    get_args()

    otsu_fusion_threshold: int = 255
    mss_fusion_threshold: int = 100
    entropy_fusion_threshold: float = 0.7

    result_image = cv2.imread(path_arg)
    original_image = cv2.imread(path_arg)

    # Perform different types of image processing
    otsu_image = otsu.otsu_and_blur(result_image, blur_amount_arg, otsu_min_threshold_arg)
    mss_image = cv2.cvtColor(mean_shift_segmentation.mss(result_image, False, 5), cv2.COLOR_RGB2GRAY)
    entropy_image = local_entropy.get_entropy_image(result_image)

    # Iterate over the processed images. Place white pixels where the images match and black pixels elsewhere
    for (i, row) in enumerate(result_image):
        for (j, pix) in enumerate(row):
            if(otsu_image[i][j] == otsu_fusion_threshold) and (mss_image[i][j] > mss_fusion_threshold) and (entropy_image[i][j] > entropy_fusion_threshold):
                result_image[i][j] = np.array([255, 255, 255])
            else:
                result_image[i][j] = np.array([0, 0, 0])

    generate_fusion_plot(original_image, result_image, otsu_image, mss_image, entropy_image)
