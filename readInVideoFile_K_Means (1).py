import cv2
import numpy as np
import time
#import vibrationController
#import textToSpeech

print('start')


def processVideoFeed():
    cap = cv2.VideoCapture('npivideo8.mp4')
    orb = cv2.ORB_create(nfeatures=350, edgeThreshold=55, nlevels=8, WTA_K=2, scaleFactor=1.2, patchSize=31, firstLevel=0, scoreType=cv2.ORB_FAST_SCORE , fastThreshold=20)
    #print("2")
    while(cap.isOpened()):
        #print("3")
        ret, frame = cap.read()
        image = frame
        cv2.imshow("Original",image)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)#convert each frame to gray
        #cv2.imshow('ORB 500',gray)
        

        ###Canny Edge Dection
        gray = cv2.Canny(gray,300,325)
        #cv2.imshow("Canny", gray)# show img with Canny

        ###ORB after Edge####
        keypoints, descriptors = orb.detectAndCompute(gray, None)
        gray = cv2.drawKeypoints(gray,keypoints,None,color=(0,255,0), flags=0)
        #cv2.imshow('ORB 25',gray)

        ### Creating Solid Black Image Mask with Smae Size as Original Image ###
        solid = np.zeros((gray.shape[0], gray.shape[1], 3), np.uint8)# numpy array same size as img
        solid[:] = (0, 0, 0)# making shape all black

        ### Plotting Points on Mask ###
        solid_pts = cv2.drawKeypoints(solid,keypoints,None,color=(0,255,0), flags=0)# draw keypoints on black image for K-means
        #cv2.imshow('ORB No Background', solid_pts)# show black img with ORB

        ### K-Means Implementation ###
        height = np.size(solid, 0)# Height of Image
        width = np.size(solid, 1)# Width of Image
        thresholdHeight = int((2/3)*height)# 1/3 Threshold from Image Bottom
        left = int((1/3)*width)# 1/3 from Left
        middle = int((2/3)*width)# 2/3 from Left
        try:
            pts = np.asarray([[p.pt[0], p.pt[1]] for p in keypoints])# convert keypoints array to array of points
            pts = np.float32(pts)# convert array to float32 for K-means
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 5, 1.0)# set maximum number of iterations and maximum accuracy before algorithm is stopped
            ret,label,center=cv2.kmeans(pts,15,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)# K-means using criteria and returning 20 points
        
            ### Plotting K-Means Centers ###
            for point in center:# Iterating through points in K-means center array
                cv2.circle(solid_pts,tuple(point),5,(0,0,255))# drawing circles for K-means centers
            #cv2.imshow("ORB with K-Means Centers", solid_pts)# Display K-means centers

            for point in center:# Iterating through points in K-means center array
                cv2.circle(gray,tuple(point),5,(0,0,255))# drawing circles for K-means centers
        #cv2.imshow("K-Means Centers Only", gray)
        except:
            input("")
            print('error')
            #continue
            
        ### Finding Image Regions ##
        

        #cv2.line(solid,(left,0),(left,height),(255,0,0),2)# Plotting Left Threshold Region
        #cv2.line(solid,(middle,0),(middle,height),(255,0,0),2)# Middle & Right Threshold Regions
        #cv2.line(solid,(0,thresholdHeight),(width,thresholdHeight),(255,0,0),2)# Bottom Threshold Region
        #cv2.imshow("K-Means Lines", solid)# Show Image with Lines
        
        cv2.line(gray,(left,0),(left,height),(255,0,0),2)# Plotting Left Threshold Region
        cv2.line(gray,(middle,0),(middle,height),(255,0,0),2)# Middle & Right Threshold Regions
        cv2.line(gray,(0,thresholdHeight),(width,thresholdHeight),(255,0,0),2)# Bottom Threshold Region
        cv2.imshow("K-Means Lines", gray)# Show Image with Lines

        ### Obstacle Flags ###
        leftObstacle = 0
        midObstacle = 0
        rightObstacle = 0
        try:
            ### Flagging Obstacles ###
            for point in center:# Iterating through points in K-means center array
                (widthPosition,heightPosition) = point
                widthPosition = int(widthPosition)
                heightPosition = int(heightPosition)
                if heightPosition >= thresholdHeight:
                    if widthPosition <= left:
                        leftObstacle = 1
                    elif left < widthPosition <= middle:
                        midObstacle = 1
                    else:
                        rightObstacle = 1
        except:
            print('error')
                    
        print("Left",leftObstacle)
        print("Right",rightObstacle)
        print("Mid",midObstacle)

        ### VERY CRUDE - Need to Fix - Just for Basic Testing ###
        ### Block to Check Obstacle Locations and Provide Feedback ###
        if leftObstacle == rightObstacle == midObstacle == 0:
            #textToSpeech.TextToSpeech("Continue Straight")
            print("Continue Straight.")
        elif rightObstacle == 0 & (leftObstacle & midObstacle == 1):
            #textToSpeech.TextToSpeech("Go Right")
            #vibrationController.obstruction("right")
            print("Go Right.")
        elif midObstacle == 0 & (leftObstacle & rightObstacle == 1):
            #textToSpeech.TextToSpeech("Continue Straight")
            print("Continue Straight.")
        elif leftObstacle == 0 & (rightObstacle & midObstacle == 1):
            #textToSpeech.TextToSpeech("Go Left")
            #vibrationController.obstruction("left")
            print("Go Left.")
        elif leftObstacle & rightObstacle & midObstacle == 1:
            #textToSpeech.TextToSpeech("STOP")
            #vibrationController.distanceSensorObstruction()
            print("STOP!")

        time.sleep(.05)
        input("")
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    processVideoFeed()
    pass
