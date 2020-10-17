import argparse
import os
import sys
import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib
import pywt

import mean_shift_segmentation
import otsu
import local_entropy
import wavelet_decomposition

path_arg: str
blur_amount_arg: int = 11
otsu_min_threshold_arg: int = 125


def get_args():
    global path_arg, blur_amount_arg, otsu_min_threshold_arg
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(help='Subcommands', dest='subcommand')

    o_mss_le = subparsers.add_parser('o_mss_le', help='Subcommand for otsu/mean shift segmentation/ local entropy fusion')
    o_mss_le.add_argument("image_path",
                          help='Directory containing images to be processed or a path to an image to be processed', type=str)
    o_mss_le.add_argument("--blur_amount", "-b",
                          help='The amount the image will be gaussian blurred. (Must be an odd number) ', type=int)
    o_mss_le.add_argument("--otsu_threshold", "-t",
                          help='The minimum threshold for the otsu algorithm.', type=int)

    wavelet_parser = subparsers.add_parser('wavelet', help='Subcommand for wavelet decomposition fusion')
    wavelet_parser.add_argument("image_path",
                                help='Directory containing images to be processed or a path to an image to be processed', type=str)

    args = parser.parse_args()
    subcommand = args.subcommand

    # Check if image path exists and is an image file type
    if os.path.exists(args.image_path):
        if not os.path.splitext(args.image_path)[1] in ['.png', '.jpeg', '.jpg']:
            sys.exit(f"ERROR: '{args.image_path}' is not an image.")
        else:
            path_arg = args.image_path
    else:
        sys.exit(f"ERROR: '{args.image_path}' does not exist")

    if subcommand == 'o_mss_le':
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

        process_subcommand_o_mss_le()
    elif subcommand == 'wavelet':
        process_subcommand_wavelet()


def process_subcommand_o_mss_le():
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


def process_subcommand_wavelet():
    original_image = cv2.imread(path_arg)
    result_image = np.copy(original_image)


    mss_image = cv2.cvtColor(mean_shift_segmentation.mss(result_image, False, 5), cv2.COLOR_RGB2GRAY)
    LL, LH, HL, HH = wavelet_decomposition.wavelet_decomposition(cv2.cvtColor(original_image, cv2.COLOR_RGB2GRAY), "db1")

    print(LL.shape)

    # Resize decomposed images to orignal size
    LL = cv2.resize(LL, (128, 128), interpolation=cv2.INTER_NEAREST)
    LH = cv2.resize(LH, (128, 128), interpolation=cv2.INTER_NEAREST)
    HL = cv2.resize(HL, (128, 128), interpolation=cv2.INTER_NEAREST)
    HH = cv2.resize(HH, (128, 128), interpolation=cv2.INTER_NEAREST)


    plt.imshow(LL, interpolation="nearest", cmap=plt.cm.gray)
    plt.show()

    sys.exit()


    # Iterate over the processed images. Place white pixels where the images match and black pixels elsewhere
    for (i, row) in enumerate(result_image):
        for (j, pix) in enumerate(row):
            pass


def generate_fusion_plot(original: np.ndarray, result: np.ndarray, otsu: np.ndarray, mss: np.ndarray, entropy: np.ndarray):
    image_name: str = os.path.basename(os.path.normpath(path_arg))
    image_name = os.path.splitext(image_name)[0]

    f, axes = plt.subplots(nrows=2, ncols=3, sharex=False, sharey=False)
    f.set_size_inches(10, 5)
    f.suptitle(image_name, fontsize=16)

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
        save_name: str = f"{image_name}-blur_{blur_amount_arg}-otsu_threhsold_{otsu_min_threshold_arg}-fusion"
        plt.savefig(f"{save_name}.png")
        plt.close()
    else:
        plt.show()


if __name__ == '__main__':
    matplotlib.use("TkAgg")     # Use TkAgg rendering backend for matplotlib
    #get_args()
    path_arg = "image_processing/whel.png"
    process_subcommand_wavelet()
