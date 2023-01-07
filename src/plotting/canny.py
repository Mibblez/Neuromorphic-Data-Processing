import cv2
from matplotlib import pyplot as plt
import argparse
import ntpath
import os

from plotting_utils.plotting_helper import path_arg, file_arg


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("image_path", help="path to image to perform edge detection on", type=file_arg)
    parser.add_argument(
        "--show_plot",
        help="shows the plot",
        action="store_true",
    )
    parser.add_argument("--save_directory", "-d", help="Save file to directory", type=path_arg, default=".")

    return parser.parse_args()


def main(args: argparse.Namespace):
    img = cv2.imread(args.image_path, 0)
    edges = cv2.Canny(img, 100, 200)

    plt.subplot(121), plt.imshow(img, cmap="gray")
    plt.title("Original Image"), plt.xticks([]), plt.yticks([])
    plt.subplot(122), plt.imshow(edges, cmap="gray")
    plt.title("Edge Image"), plt.xticks([]), plt.yticks([])

    image_name = os.path.splitext(ntpath.basename(args.image_path))[0]

    plt.savefig(os.path.join(args.save_directory, f"Canny-{image_name}.png"))
    plt.clf()


if __name__ == "__main__":
    args = get_args()
    main(args)
