import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import cv2

import pywt
import pywt.data


def wavelet_decomposition(img: np.ndarray, wavelet_type: str = "db4"):
    coeffs2 = pywt.dwt2(img, wavelet_type)
    LL, (LH, HL, HH) = coeffs2

    return LL, LH, HL, HH


if __name__ == "__main__":
    matplotlib.use("TkAgg")

    original = cv2.imread("whel.png")
    original = cv2.cvtColor(original, cv2.COLOR_RGB2GRAY)

    LL, LH, HL, HH = wavelet_decomposition(original)
    print(LL.shape)

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

    fig.tight_layout()
    plt.show()
