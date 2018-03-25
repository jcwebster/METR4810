'''John Webster
19 Mar 2018
## GCM FSM definition
'''
'''
TODO:
fix Manual steering getch() implementation to increment counter and exit
'''
from msvcrt import getch
import time

#STATES
MENU = 0
CALIBRATION = 1
POWER_CYCLING = 2
MANUAL = 3
NAVIGATE_TO = 4

state = 0

#calibration variables
finished = 0

#steering variables
counter = 0

#power cycle variables
opower_state = 0
ipower_state = 0

def calibrate():
    print("Calibration mode\n")
    #calibrate here...
    
    global finished
    finished = 1
    
def power_cycle():

    opower_state = 0 # get orientation power state here
    ipower_state = 0 # get imaging power state here
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
            # Set orientation power state here
            
            opower_state = int(not opower_state)

        elif system_select == 'i':
            print("Toggling power on imaging system...\n")
            # Set imaging power state here
            
            ipower_state = int(not ipower_state)
            
        elif system_select == 'e':
            #exit and return to menu
            return
        
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
    print("Steering mode (press 'm' to return to main menu):\n")
    key = 0
    #key = ord(getch())
    print(key)

    angleStep = 10
    pitch = 0
    roll = 0
    yaw = 0
    
    done = 0

    #imagine delay in sending any initial command...

    #press a key to count up or down, j\k to adjust increment size...
    #and display a counter value in degrees on screen: that value will be
    #the degree increment command that is sent to the telescope
    while ((not (key == 'm')) or (not done)):
        key = raw_input()
       # key = ord(getch())
        #print(key)
##        while (raw_input() == key):
##            counter = counter + 1
##            print(str(counter) + '\r')
##        degrees = counter * k #k is some scaling factor to convert counter value to degrees

        if (key == 'w'):
            pitch = pitch + angleStep
        elif (key == 's'):
            pitch = pitch - angleStep
        elif (key == 'd'):
            yaw = yaw + angleStep
        elif (key == 'a'):
            yaw = yaw - angleStep
        elif (key == 'e'):
            roll = roll + angleStep
        elif (key == 'q'):
            roll = roll - angleStep
        elif (key == 'j'):         #else change angleStep size
            angleStep = angleStep / 2
        elif (key == 'k'):
            angleStep = angleStep * 2

        print("Pitch: " + str(pitch) + " Yaw: " + str(yaw)\
              + " Roll: " + str(roll) + '\r')

        if (key == ""):
            print('\nMove ' + "Pitch: " + str(pitch) + " Yaw: " + str(yaw)\
              + " Roll: " + str(roll) + ' (deltas)? (y/n to confirm)')

            decision = 0

            while (not(decision == 'y') or (decision == 'n')):
                decision = raw_input()

            if (decision == 'y'):
                #[code move here]
                print('Moving ...')
                time.sleep(1)
                done = 1
                print('done')
                return
            elif (decision == 'n'):
                #retry entry
                print("Send a new move command: ")
                
            
    
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

        print("Now exiting manual steering mode")

        state = MENU

    elif state == NAVIGATE_TO:
        #enter point to point navigation mode
        print("Navigate to...")

        time.sleep(1)
        state = MENU

        #exit when....
##    state = int(raw_input())

        
