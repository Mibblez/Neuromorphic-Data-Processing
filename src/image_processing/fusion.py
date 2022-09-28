import argparse
import os
import sys
import math
import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib

import mean_shift_segmentation
import otsu
import local_entropy
import wavelet_decomposition

path_arg: str = ''
blur_amount_arg: int = 11
otsu_min_threshold_arg: int = 125


def get_args():
    global path_arg, blur_amount_arg, otsu_min_threshold_arg
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(help="Subcommands", dest="subcommand")

    o_mss_le = subparsers.add_parser(
        "o_mss_le", help="Subcommand for otsu/mean shift segmentation/ local entropy fusion"
    )
    o_mss_le.add_argument(
        "image_path", help="Directory containing images to be processed or a path to an image to be processed", type=str
    )
    o_mss_le.add_argument(
        "--blur_amount", "-b", help="The amount the image will be gaussian blurred. (Must be an odd number) ", type=int
    )
    o_mss_le.add_argument("--otsu_threshold", "-t", help="The minimum threshold for the otsu algorithm.", type=int)

    wavelet_parser = subparsers.add_parser("wavelet", help="Subcommand for wavelet decomposition fusion")
    wavelet_parser.add_argument(
        "image_path", help="Directory containing images to be processed or a path to an image to be processed", type=str
    )

    args = parser.parse_args()
    subcommand = args.subcommand

    # Check if image path exists and is an image file type
    if os.path.exists(args.image_path):
        if not os.path.splitext(args.image_path)[1] in [".png", ".jpeg", ".jpg"]:
            sys.exit(f"ERROR: '{args.image_path}' is not an image.")
        else:
            path_arg = args.image_path
    else:
        sys.exit(f"ERROR: '{args.image_path}' does not exist")

    if subcommand == "o_mss_le":
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
    elif subcommand == "wavelet":
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
            if (
                (otsu_image[i][j] == otsu_fusion_threshold)
                and (mss_image[i][j] > mss_fusion_threshold)
                and (entropy_image[i][j] > entropy_fusion_threshold)
            ):
                result_image[i][j] = np.array([255, 255, 255])
            else:
                result_image[i][j] = np.array([0, 0, 0])

    fig_title: str = os.path.splitext(os.path.basename(os.path.normpath(path_arg)))[0]
    save_name: str = f"{fig_title}-blur_{blur_amount_arg}-otsu_threhsold_{otsu_min_threshold_arg}-fusion"
    create_fusion_plot(
        fig_title,
        save_name,
        [original_image, result_image, [], otsu_image, mss_image, entropy_image],
        ["Orignal", "Fusion Image", "", "Gaussian Blur Otsu", "Mean Shift", "Entropy"],
    )


def wavelet_combine(original, mss, decomp, low_thresh, high_thresh, mss_thresh) -> np.ndarray:
    result_image = np.copy(original)
    for (i, row) in enumerate(result_image):
        for (j, pix) in enumerate(row):
            if (mss[i][j] > mss_thresh) and (decomp[i][j] > high_thresh or decomp[i][j] < low_thresh):
                result_image[i][j] = np.array([255, 255, 255])
            else:
                result_image[i][j] = np.array([0, 0, 0])
    return result_image


def create_fusion_plot(fig_title: str, save_name: str, images: list, titles: list):
    if len(images) != len(titles):
        raise Exception("images list and titles list bust be of the same length")

    num_images: int = len(images)
    plot_rows: int = 2
    plot_columns: int = math.ceil(float(num_images) / float(plot_rows))

    f, axes = plt.subplots(nrows=plot_rows, ncols=plot_columns, sharex=False, sharey=False)
    f.set_size_inches(10, 5)
    f.suptitle(fig_title, fontsize=16)

    plt.gray()  # Set default colormap to grayscale
    plt.tight_layout()

    for i in range(plot_rows):
        for j in range(plot_columns):
            image: np.ndarray = images.pop(0)
            title: str = titles.pop(0)

            if title == "" or (image.size == 0):
                axes[i, j].remove()
            else:
                axes[i, j].imshow(image)
                axes[i, j].set_title(title)
                axes[i, j].axis("off")

    plt.savefig(save_name)
    plt.close


def process_subcommand_wavelet():
    mss_fusion_threshold: int = 100
    wavelet_threshold_low: int = -100
    wavelet_threshold_high: int = 100
    wavelet_type: str = "db1"

    original_image = cv2.imread(path_arg)
    result_image = np.copy(original_image)

    mss_image = cv2.cvtColor(mean_shift_segmentation.mss(result_image, False, 5), cv2.COLOR_RGB2GRAY)
    LL, LH, HL, HH = wavelet_decomposition.wavelet_decomposition(
        cv2.cvtColor(original_image, cv2.COLOR_RGB2GRAY), wavelet_type
    )

    # Resize decomposed images to orignal size
    LL = cv2.resize(LL, (128, 128), interpolation=cv2.INTER_NEAREST)
    LH = cv2.resize(LH, (128, 128), interpolation=cv2.INTER_NEAREST)
    HL = cv2.resize(HL, (128, 128), interpolation=cv2.INTER_NEAREST)
    HH = cv2.resize(HH, (128, 128), interpolation=cv2.INTER_NEAREST)

    # Iterate over the processed images. Place white pixels where the images match and black pixels elsewhere
    HH_result = wavelet_combine(
        original_image, mss_image, HH, wavelet_threshold_low, wavelet_threshold_high, mss_fusion_threshold
    )
    LH_result = wavelet_combine(
        original_image, mss_image, LH, wavelet_threshold_low, wavelet_threshold_high, mss_fusion_threshold
    )
    HL_result = wavelet_combine(
        original_image, mss_image, HL, wavelet_threshold_low, wavelet_threshold_high, mss_fusion_threshold
    )

    image_name: str = os.path.basename(os.path.normpath(path_arg))
    image_name = os.path.splitext(image_name)[0]
    save_name = f"{image_name}_wavelet_fusion_{wavelet_type}"

    create_fusion_plot(
        image_name,
        save_name,
        [original_image, mss_image, HH, HH_result, LH, LH_result, HL, HL_result],
        ["Orignal", "Mean Shift", "HH", "HH_result", "LH", "LH_result", "HL", "HL_result"],
    )


if __name__ == "__main__":
    matplotlib.use("TkAgg")  # Use TkAgg rendering backend for matplotlib
    get_args()
