import cv2
from matplotlib import pyplot as plt
from sklearn.ensemble import IsolationForest

img = cv2.imread("pol.png",0)
img2 = cv2.imread("pol2.png",0)

orb = cv2.ORB_create(nfeatures=2000)
keypoints, descriptors = orb.detectAndCompute(img, None)#get dots
img = cv2.drawKeypoints(img, keypoints, None) #put dots on img
keypoints2, descriptors2 = orb.detectAndCompute(img, None)#get dots
img2 = cv2.drawKeypoints(img2, keypoints, None) #put dots on img

xyTrain = []
for x in keypoints2:
    xyTrain.append(x.pt)

clf = IsolationForest(max_samples=100, random_state=10, behaviour="new", contamination=.1)
clf.fit(keypoints2)
test = clf.predict(keypoints)

#dst = cv2.fastNlMeansDenoising(img,img2, 1, 1, 100000)
plt.subplot(121),plt.imshow(img)
plt.subplot(122),plt.imshow(img2)
plt.show()