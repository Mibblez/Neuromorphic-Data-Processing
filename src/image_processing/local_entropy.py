"""Image processing calculations for Local Entropy for event detected images"""

import matplotlib.pyplot as plt
import numpy as np
import os
import argparse
from PIL import Image

from plotting_utils.plotting_helper import path_arg, file_arg


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Entropy Calculation", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("image_file", type=file_arg, help="Image file to be processed")
    parser.add_argument(
        "--save_directory",
        "-d",
        type=path_arg,
        default=".",
        help="Path where the image after processing is to be saved to",
    )
    parser.add_argument("--save_img", action="store_true", help="Save image without plot information")
    parser.add_argument(
        "--exclude_plot", dest="save_plot", action="store_false", help="Save image with plot information"
    )
    parser.add_argument("--save_entropy_data", action="store_true", help="Save entropy data for each image in a CSV")
    args = parser.parse_args()

    if not os.path.splitext(args.image_file)[1] in (".png", ".jpeg", ".jpg"):
        parser.error(f"ERROR: '{args.image_file}' is not an image.")

    if not args.save_plot and not (args.save_entropy_data or args.save_img):
        parser.error("ERROR: --save_entropy_data or --save_img must be set if excluding plot.")

    return args


# Convert an rgb image to a grayscale image
def rgb2gray(rgb: np.ndarray) -> np.ndarray:
    return np.dot(rgb[..., :3], [255 * 0.2989, 255 * 0.5870, 255 * 0.1140])


# Calculate entropy. Returns the entropy of a signal - signal must be a 1-D numpy array
def entropy(signal: np.ndarray) -> np.float64:
    lensig = signal.size
    symset = list(set(signal))
    propab = [np.size(signal[signal == i]) / (1.0 * lensig) for i in symset]
    ent = np.sum([p * np.log2(1.0 / p) for p in propab])
    return ent


def get_entropy_image(img: np.ndarray, convert_to_gray=True) -> np.ndarray:
    if convert_to_gray:
        img = rgb2gray(img)

    N = 5
    S = img.shape
    E = np.array(img)

    for row in range(S[0]):
        for col in range(S[1]):
            Lx = np.max([0, col - N])
            Ux = np.min([S[1], col + N])
            Ly = np.max([0, row - N])
            Uy = np.min([S[0], row + N])
            region = img[Ly:Uy, Lx:Ux].flatten()
            E[row, col] = entropy(region)

    return E


def main(args: argparse.Namespace):
    # Grab filename from path
    file_name = os.path.basename(os.path.normpath(args.image_file))
    file_name = os.path.splitext(file_name)[0]

    # Image must read in as RGB and manually converted to grayscale with rgb2gray
    image = np.array(Image.open(args.image_file).convert("RGB"))

    entropy = get_entropy_image(image)
    entropy_sum = entropy.sum()

    if args.save_img:
        # Save the entropy images
        image_save_path = os.path.join(args.save_directory, f"LocalEntropy_img_{file_name}")
        plt.imsave(image_save_path, entropy, cmap="viridis")

    if args.save_plot:
        # Save the entropy figures
        fig, (ax0) = plt.subplots(nrows=1, ncols=1, figsize=(12, 5))
        ax0.imshow(entropy, cmap="viridis")
        ax0.set_title("Local entropy Image, Entropy=" + str(round(entropy_sum, 3)), fontsize=10)
        plt.colorbar(ax0.imshow(entropy, cmap="viridis"), ax=ax0, fraction=0.046, pad=0.04)
        full_path_fig = os.path.join(args.save_directory, f"LocalEntropy_fig_{file_name}")
        fig.savefig(full_path_fig, bbox_inches="tight")
        plt.close(fig)

    if args.save_entropy_data:
        # Save csv with local entropy values of each image
        full_csv_path = os.path.join(args.save_directory, "LocalEntropy_data.csv")

        # Append to the csv if it exists. Otherwise create it and make the first entry
        if os.path.exists(full_csv_path):
            with open(full_csv_path, "a", newline="") as csv_file:
                csv_file.write(f"{os.path.normpath(args.image_file)},{entropy_sum}\n")
        else:
            with open(full_csv_path, "w", newline="") as csv_file:
                csv_file.write("File Name,Local Entropy\n")
                csv_file.write(f"{os.path.normpath(args.image_file)},{entropy_sum}\n")


if __name__ == "__main__":
    args = get_args()
    main(args)
