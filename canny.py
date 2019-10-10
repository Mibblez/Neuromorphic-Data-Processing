import cv2
import numpy as np
from matplotlib import pyplot as plt

img = cv2.imread('imageData/foam 10hz 30 deg time based Frames/foam 10hz 30 deg0.png',0)
edges = cv2.Canny(img,100,200)

plt.subplot(121),plt.imshow(img,cmap = 'gray')
plt.title('Original Image'), plt.xticks([]), plt.yticks([])
plt.subplot(122),plt.imshow(edges,cmap = 'gray')
plt.title('Edge Image'), plt.xticks([]), plt.yticks([])

plt.show()