##NETR4810:: THE JOHN TEBBUTT SPACE TELESCOPE
##GROUND_CONTROL_MODULE SOFTWARE
##30 Mar 2018
##Author: John Webster

'''TODO:
- test 'send-command' fnction 
'''


'''*********************************************'''        
'''              IMPORTS                        '''
'''*********************************************'''
from __future__ import print_function
import os
##import numpy as np
##import cv2
import time
import serial


'''*********************************************'''        
'''              VARIABLE DECLARTIONS           '''
'''*********************************************'''
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


a = 0

'''*********************************************'''        
'''              FUNCTION DEFINITIONS           '''
'''*********************************************'''

def send_command(mode, command):
        #this function sends a command through the DSN block following protocol, \
        # and then once it receives the command from the DSN block, it transmits \
        # it through the bluetooth serial port
    if (mode == 1): #calibration
        cp2102_ser.writelines(command)
#CAUTION: need to implement a wait or while loop for reading?
        while (data_to_send == None):
            pass
        data_to_send = cp2102_ser.readline();

        #send data that was received 
        bt_ser.writeline(data_to_send)
        
'''
    elif (mode == 2):
    
    elif (mode == 3):
            
    elif (mode == 4):

    else:
        break
'''

def calibrate():
    print("Calibration mode\n")
    #calibrate here...
    
    global finished
    finished = 1
    
def power_cycle():

    opower_state = 0 # get orientation power state here
    ipower_state = 0 # get imaging power state here
    print("Select a system to power cycle (press 'm' to exit): \n\
                'p': Power on all subsystems \n\
                'o': Orientation control \n\
                'i': Imaging system \n ")
    system_select = raw_input()

    while (not(system_select == 'm')):

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
        print("Select a system to power cycle (press 'm' to exit): \n\
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
    while ((not (key == 'm')) and (not done)):
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
    print("Navigate to point.....\n(press 'm' to return to main menu):\n")
    #calculate angle of declination and right ascension here
    angleStep = 10
    pitch = 0
    roll = 0
    yaw = 0
    key = '0'
    
    done = 0

    while (not (key == 'm'))
        print("Enter angle of right ascension: ")
        ra = raw_input()
        print("Enter angle of declination")
        dec = raw_input()

        if (ra == 'm' or dec = 'm')
                break
        

    
def save_image():
    bt_ser.write('x')
    print("Capturing image...\n")

    #wait for and receive iamge save ACKnowledgement
    while (not bt_ser.readline())
    
    print("Mission successful = " + bt_ser.readline())
    

'''*********************************************'''        
'''              INITIALISATIONS                '''
'''*********************************************'''
#configure serial connection
cp2102_ser = serial.Serial(
    port='COM3',\ #consider replacing COM3 with a str variable
    baudrate=9600,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=0)              #computer to CP2102 serial port, used for interfacing with the DSN block 10sec delay

bt_ser = serial.Serial(
    port='COM5',\
    baudrate=9600,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=0)              #Bluetooth to computer serial port connection, used to transmit and receieve commands from the telescope

if ((cp2102_ser.isOpen()) and (bt_ser.isOpen())):
        
    print("Computer CP2102 connected to: " + ser1.portstr)
    print("Bluetooth HC06 connected to: " + ser2.portstr)
else
    print("Failed to open a serial port")



'''*********************************************'''        
'''              MAIN EXECUTIVE                 '''
'''*********************************************'''
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
