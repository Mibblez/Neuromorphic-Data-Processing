import cv2
import numpy as np
from matplotlib import pyplot as plt
import argparse
import ntpath
import os

show_plot = True
save_fig = False
image_path = ''

def get_args():
    global show_plot, save_fig, image_path

    parser = argparse.ArgumentParser()

    parser.add_argument('image_path', help='path to image to perform edge detection on', type=str)
    parser.add_argument('--hide_plot', '-h', help='prevents the plot from being shown', action='store_true')
    parser.add_argument('--save_fig', '-s', help='saves the figure to disk', action='store_true')

    args = parser.parse_args()

    show_plot = not args.hide_plot
    save_fig = args.save_fig
    image_path = args.image_path

if __name__ == '__main__':
    get_args()

    img = cv2.imread(image_path,0)
    edges = cv2.Canny(img,100,200)

    plt.subplot(121),plt.imshow(img,cmap = 'gray')
    plt.title('Original Image'), plt.xticks([]), plt.yticks([])
    plt.subplot(122),plt.imshow(edges,cmap = 'gray')
    plt.title('Edge Image'), plt.xticks([]), plt.yticks([])

    image_name = os.path.splitext(ntpath.basename(image_path))[0]

    if save_fig:
        plt.savefig(os.path.join(f'Canny-{image_name}.png'))

    if show_plot:
        plt.show()
    else:
        plt.clf()