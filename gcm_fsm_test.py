'''John Webster
19 Mar 2018
## GCM FSM definition
'''

import time

#STATES
MENU = 0
CALIBRATION = 1
POWER_CYCLING = 2
MANUAL = 3
NAVIGATE_TO = 4

state = 0
finished = 0

opower_state = 0
ipower_state = 0

def calibrate():
    
    print("Calibration mode\n")

    global finished
    finished = 1
    
def power_cycle():

    opower_state = 0 # get and set  orientation power state here
    ipower_state = 0 # get and set imaging power state here
    print("Select a system to power cycle (press 'e' to exit): \n\
                'p': Power on all subsystems \n\
                'o': Orientation control \n\
                'i': Imaging system \n ")
    system_select = raw_input()

    while (not(system_select == 'e')):

        if system_select == 'p':
            print("All systems will be rebooted now...")

            print("systems off\n")

            time.sleep(1)
            print("systems on\n")
            
        elif system_select == 'o':
            print("Toggling power on orientation control system...\n")

            opower_state = int(not opower_state)

        elif system_select == 'i':
            print("Toggling power on imaging system...\n")

            ipower_state = int(not ipower_state)
            
        elif system_select == 'e':
            state = 'm'
            return (state)
        
        print("Orientation system powered: " + str(opower_state))
        print("Imaging system powered: " + str(ipower_state) + "\n\n")

        time.sleep(1)
        print("Select a system to power cycle (press 'e' to exit): \n\
                'p': Power on all subsystems \n\
                'o': Orientation control \n\
                'i': Imaging system \n ")
        system_select = raw_input()

    global state
    state = 0
    return

 
def manual_steer():
    print("Steering mode\n")
    #how to cycle through and send commands to minimize annoyance of delay?
    key = raw_input()

    while (key (not 'm')):
        key = raw_input()

        #control manually
    
def navigate_to():
    print("Navigate to point.....")

    
def save_image():
    print("Capturing image...\n")
	
 	
##def mode_select(argument):
##    switcher = {
##            1: calibrate,
##            2: power_cycle ,
##            3: manual_steer,
##            4: navigate_to,
##            5: save_image
##    }
##    #get function from switcher dictionary
##    func = switcher.get(argument, default = "nothing")
##    #execute the function
##    func()

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
        state = int(raw_input())
        
        
    elif state == CALIBRATION:
        #enter Calibration mode
        print("Now in calibration mode: ")
        calibrate()

        time.sleep(1)
        if finished:
            state = MENU
            print("done")
        #exit if interrupt 'm' is received or finished
    elif state == POWER_CYCLING:
        #enable power cycling
        print("Now in power cycling mode: ")

        power_cycle()
        #exit if key 'e' is received or alternate key
        #state = int(raw_input())

    elif state == MANUAL:
        #enable free steering
        print("Now in manual steering mode")
        manual_steer()

        state = MENU

    elif state == NAVIGATE_TO:
        #enter point to point navigation mode
        print("Navigate to...")

        time.sleep(1)
        state = MENU

        #exit when....
##    state = int(raw_input())

        
