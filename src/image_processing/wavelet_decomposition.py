import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import cv2

import ntpath
import argparse
import os

import pywt
import pywt.data

from plotting_utils.plotting_helper import path_arg, file_arg_image


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("image_path", help="path to image to perform wavelet decomposition on", type=file_arg_image)
    parser.add_argument(
        "--type",
        "-t",
        help="sets the type of wavelet decomposition to perform",
        action="store",
        type=str
    )
    parser.add_argument("--save_directory", "-d", help="Save file to directory", type=path_arg, default=".")
    args = parser.parse_args()
    if args.type not in pywt.wavelist():
        parser.error("Error: Invalid wavelet type")

    return parser.parse_args()


def wavelet_decomposition(img: np.ndarray, wavelet_type: str):
    coeffs2 = pywt.dwt2(img, wavelet_type)
    LL, (LH, HL, HH) = coeffs2

    return LL, LH, HL, HH


def main(args: argparse.Namespace):
    matplotlib.use("TkAgg")

    image = cv2.imread(args.image_path)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    LL, LH, HL, HH = wavelet_decomposition(image, args.type)

    # Wavelet transform of image, and plot approximation and details
    titles = ["Approximation", " Horizontal detail", "Vertical detail", "Diagonal detail"]

    fig = plt.figure(figsize=(12, 3))
    for i, a in enumerate([LL, LH, HL, HH]):
        print(a.shape)
        ax = fig.add_subplot(1, 4, i + 1)
        ax.imshow(a, interpolation="nearest", cmap=plt.cm.gray)
        ax.set_title(titles[i], fontsize=10)
        ax.set_xticks([])
        ax.set_yticks([])

    image_name = os.path.splitext(ntpath.basename(args.image_path))[0]

    fig.tight_layout()
    plt.savefig(os.path.join(args.save_directory, f"WaveletDecomp-{args.type}-{image_name}.png"))


if __name__ == "__main__":
    args = get_args()
    main(args)
