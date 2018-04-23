##contains two test files. see older version commented out below
import cv2
import time

#1. Create an object. Zero for external camera: actually brings up prompt to select camera. 1 starts webcam (no image)
video = cv2.VideoCapture(0)
success = video.isOpened()

if not success:
	print("Camera open fail")

# camera config - only affects facetime camera
video.set(cv2.CAP_FFMPEG, True)
video.set(cv2.CAP_PROP_FPS, 30)
#video.set(cv2.CAP_PROP_MODE, CV_CAP_MODE_YUYV)

# Global Variables
font = cv2.FONT_HERSHEY_PLAIN
a=0
width = video.get(cv2.CAP_PROP_FRAME_WIDTH) #float
height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)  #float

#define crosshairs size
lineLength = 25
xL = int((width - lineLength) / 2)
xR = int(xL + lineLength)
xT = int((height - lineLength) / 2)
xB = int(xT + lineLength)

while video.isOpened():
	
	# #get keyboard input
	# input = raw_input(">> ")
	# if input == 'exit':
	# 	ser.close()
	# 	exit()
	# else:
	# 	#send character back out; or send character as argument to mode_select
	# 	ser.write(input)
	# 	out = ""
	# 	time.sleep(1)
	# 	while ser.inWaiting() > 0:
	# 		out += ser.read(1)
	# 	
	# 	if out != "":
	# 		print(">>" + out)
	# 		
	a = a + 1
	
	#3. Create a frame object.
	check, frame = video.read()
	
	print ("width: " + str(width))
	print ("height: " + str(height))
	# print(check)
	# print(frame) # representing image
	
	#6. Converting to grayscale
	
	grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	
	#4. Show the frame!! after drawing the lines*
	cv2.line(img=frame, pt1=(xL, int(height/2)), pt2=(xR, int(height/2)), color=(0, 255, 0), thickness=1, lineType=8, shift=0)
	cv2.line(img=frame, pt1=(int(width/2), xT), pt2=(int(width/2), xB), color=(0, 255, 0), thickness=1, lineType=8, shift=0)
	cv2.putText(frame, "width: " +str(width), (10,455), 1, font, (255,255,255))
	cv2.putText(frame, "height: " + str(height), (10,475), 1, font, (255,255,255))
	if check:	
		cv2.imshow("Capturing", frame)
		
		cv2.line(img=grey, pt1=(xL, int(height/2)), pt2=(xR, int(height/2)), color=(0, 255, 0), thickness=1, lineType=8, shift=0)
		cv2.line(img=grey, pt1=(int(width/2), xT), pt2=(int(width/2), xB), color=(0, 255, 0), thickness=1, lineType=8, shift=0)
		cv2.putText(grey, "width: " +str(width), (10,455), 1, font, (255,255,255))
		cv2.putText(grey, "height: " + str(height), (10,475), 1, font, (255,255,255))
		cv2.imshow("greyscale", grey)

	#5. For press any key to advance frame (milliseconds)
	#cv2.waitKey(0)
	
	#7. For playing
	key = cv2.waitKey(1)
	
	if key == ord('q'):
		break
	# else:
	# 	cv2.line(img=frame, pt1=(10, 100), pt2=(20, 10), color=(255,255,0), thickness=5, lineType=8, shift=0)
	
print(a)

#2. Shutdown the camera
video.release()
print ("ending: " + str(width))

cv2.destroyAllWindows


##import cv2, time
###1. Create an object. Zero for external camera
##
##video = cv2.VideoCapture(0)
##success = video.isOpened()
##print 'hi'
##print( 'success='  + str(success) )
##
###8. a variable
##a=0
##
##while True:
##	
##	a = a + 1
##	
##	#3. Create a frame object.
##	check, frame = video.read()
##	
##	print(check)
##	print(frame) # representing image
##	
##	#6. Conerting to grayscale
##	
##	grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
##	
##	#4. Show the frame!!
##	cv2.imshow("Capturing", grey)
##	
##	#5. For press any key to out (milliseconds)
##	#cv2.waitKey(0)
##	
##	#7. For playing
##	key = cv2.waitKey(1)
##	
##	if key == ord('q'):
##		break
##	
##print(a)
##
###2. Shutdown the camera
##video.release()
##
##cv2.destroyAllWindows
