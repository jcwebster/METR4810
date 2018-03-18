## GCM FSM definition

import time

#STATES
MENU = 0
CALIBRATION = 1
POWER_CYCLING = 2
MANUAL = 3
NAVIGATE_TO = 4

state = 0

 
def manual_steer():
    print("Steering mode\n")
 	
def calibrate():
    print("Calibration mode\n")
    
def power_cycle():
    print("Power cycling mode\n")

def navigate_to():
    print("Navigate to point.....")

    
def save_image():
    print("Capturing image...\n")
	
 	
def mode_select(argument):
    switcher = {
            1: calibrate,
            2: power_cycle ,
            3: manual_steer,
            4: navigate_to,
            5: save_image
    }
    #get function from switcher dictionary
    func = switcher.get(argument, default = "nothing")
    #execute the function
    func()

a = 0
while True:

##    for x in range(0,4):
##        mode_select(a)
##        time.sleep(1)
##        
  
    if state == MENU:
        #display menu selection and instructions
        print("Menu select: \n\
                1. Calibration \n\
                2. Subsystem power management \n\
                3. Manual free steering \n\
                4. Navigate to point")
        
    elif state == CALIBRATION:
        #enter Calibration mode
        print("Now in calibration mode: ")
        calibrate()
        

    elif state == POWER_CYCLING:
        #enable power cycling
        print("Now in power cycling mode: ")

        power_cycle()

    elif state == MANUAL:
        #enable free steering
        
        print("Manual steering enabled")
        

    elif state == NAVIGATE_TO:
        #enter point to point navigation mode
        print("Navigate to...")

    state = int(raw_input())

        
