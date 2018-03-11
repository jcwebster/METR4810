from __future__ import print_function
import os
import numpy as np

import cv2, time

#1. Create an object. Zero for external camera
video = cv2.VideoCapture(0)
success = video.isOpened()

if not success:
	print("Camera open fail")

# Global Variables
a=0
width = video.get(cv2.CAP_PROP_FRAME_WIDTH) #float
height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)  #float

while video.isOpened():
	
	a = a + 1
	
	#3. Create a frame object.
	check, frame = video.read()
	
	print ("width: " +str(width))
	print ("height: " + str(height))
	print(check)
	print(frame) # representing image
	
	#6. Converting to grayscale
	
	#grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	
	#4. Show the frame!! after drawing the line*
	cv2.line(img=frame, pt1=(100, 100), pt2=(200, 100), color=(255,0,255), thickness=50, lineType=4, shift=0)
	cv2.imshow("Capturing", frame)

	#5. For press any key to advance frame (milliseconds)
	cv2.waitKey(0)
	
	#7. For playing
	key = cv2.waitKey(1)
	
	if key == ord('q'):
		break
	else:
		cv2.line(img=frame, pt1=(10, 100), pt2=(20, 10), color=(255,255,0), thickness=5, lineType=8, shift=0)
	
print(a)

#2. Shutdown the camera
video.release()

cv2.destroyAllWindows