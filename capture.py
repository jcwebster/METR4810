import cv2, time
#1. Create an object. Zero for external camera

video = cv2.VideoCapture(1)
success = video.isOpened()
print 'hi'
print( 'success='  + str(success) )

#8. a variable
a=0

while True:
	
	a = a + 1
	
	#3. Create a frame object.
	check, frame = video.read()
	
	print(check)
	print(frame) # representing image
	
	#6. Conerting to grayscale
	
	grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	
	#4. Show the frame!!
	cv2.imshow("Capturing", grey)
	
	#5. For press any key to out (milliseconds)
	#cv2.waitKey(0)
	
	#7. For playing
	key = cv2.waitKey(1)
	
	if key == ord('q'):
		break
	
print(a)

#2. Shutdown the camera
video.release()

cv2.destroyAllWindows