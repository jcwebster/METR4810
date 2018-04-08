##NETR4810:: THE JOHN TEBBUTT SPACE TELESCOPE
##GROUND_CONTROL_MODULE SOFTWARE
##30 Mar 2018. Last rev: 060418
##Author: John Webster

'''TODO:
- NOTE: bluetooth com connection with HC06 doesn't always work right after a break in program
- test 'send-command' fnction - work with Andy for the "@andy" comments
    -need to use second usb-ttl adapter so that one can be used with the tx-rx shunt
        and the other connected to HC05/6 (pick oneeee) so that a command will be
        mirrored in the cp_ser_port and send to the bluetooth comport to test reception
        and decoding of a char
- note for @andy 2: booting the HC05 in AT mode with hardware and then sending a
            serial.write("AT+RESET")to the hc06 module on board after settings are
            configured SHOULD put the module into pairing mode and
            it should work as configured after that.
- implement send_command() for all modes of operation
    - calibration
    - manual - change xyz entry to angle of declin. and ra
    - navigate to
- need to develop calibration algorithm with andy
- need to def coords_to_send() to format angle of declin. and ra to a two byte package to send
'''

from __future__ import print_function
import os
##import numpy as np
##import cv2
import time
import serial

'''*********************************************'''        
'''              ^IMPORTS^                      '''
'''*********************************************'''

'''*********************************************'''        
'''              VARIABLE DECLARTIONS           '''
'''*********************************************'''
#communication variables
COMS_BAUD = 1200
usbTTL_COM = 'COM9'
bluetooth_COM = 'COM5'
bt_device = "HC06"
SUCCESS_ACK = 1 # NEED TO ASK ANDY WHAT CHAR HE WOULD LIKE TO SEND AS AN ACK for success or failure
WAITING_TIME = 5  # CAUTION: adjust waiting time as necessary during testing, or add a while loop
DSN_DELAY = 2

#STATES
MENU = 0
CALIBRATION = 1
POWER_CYCLING = 2
MANUAL = 3
NAVIGATE_TO = 4
SHUTDOWN = 5
SAVE = 6

state = 0

#calibration variables
finished = 0

#steering variables
counter = 0

#power cycle variables
opower_state = 0
ipower_state = 0

'''*********************************************'''        
'''              FUNCTION DEFINITIONS           '''
'''*********************************************'''
#this function sends a command through the DSN block following protocol, \
# and then once it receives the command from the DSN block, it transmits \
# it through the bluetooth serial port
def send_command(mode, command):
    if ((cp2102_ser.isOpen()) and (bt_ser.isOpen())):

        if (mode == CALIBRATION or mode == POWER_CYCLING or mode == SAVE): 
            cp2102_ser.writelines(command)
            data_to_send = None
            
            print("waiting...")
            time.sleep(DSN_DELAY) 
            data_to_send = cp2102_ser.readline()
##            #Need to test this more thoroughly
##            while (data_to_send == None):
##                #pass
##                data_to_send = cp2102_ser.readline()

            #send data that was received
            print(data_to_send + " received from DSN, sending...")
            bt_ser.writelines(data_to_send)
            time.sleep(1)
            return 1
        
        elif (mode == NAVIGATE_TO):
            
            return 1
        elif (mode == MANUAL):
            print(str(command[0]) + str(command[1]) + str(command[2]))
            print("Sending command/coords[]..")
    #CAUTION: format coordinate command correctly here before writing...
            cp2102_ser.writelines(str(command[0]) + str(command[1]))
            data_to_send = None
            
    #CAUTION: need to implement a wait or while loop for reading?
            print("waiting...")
            time.sleep(DSN_DELAY) #could remove
            
            #Need to test this more thoroughly
            while (data_to_send == None):
                data_to_send = cp2102_ser.readline()

            #send data that was received
            print(data_to_send + " received from DSN, sending...")
            bt_ser.writelines(data_to_send)
            
            return 1
        else:
            print("Invalid mode")
            return -1
    else:
        print("error opening a serial port")
        return -1


def calibrate():
    print("Calibration mode\n")
    #calibrate here...
##CAUTION: need to develop calibration algorithm
    print("Enter a char to send: \n")
    char_to_send = raw_input()

    if (send_command(CALIBRATION, char_to_send)):
        global finished
        finished = 1
    else:
        return print("Error in sending command")
    
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
            if (send_command(POWER_CYCLING, system_select) == -1):
                print("error\n")

            time.sleep(WAITING_TIME)
##            if (bt_ser.readline() == SUCCESS_ACK):
            received_data = None
            a=0
            while (received_data == None and a < 999999):
                received_data = bt_ser.readline()       #CAUTION: NEED TO FIGURE OUT WHY THIS ISN'T WORKING
                a = a + 1

            print(a)
            print( "received data: " + str(received_data))

            if (received_data == system_select): #for testing CAUTION swap back to SUCCESS_ACK above once working
                print("All subsystems power cycled, success\n")
            else:
                print("Incorrect message received from bluetooth")
            
        elif system_select == 'o':
            print("Toggling power on orientation control system...\n")

            if (send_command(POWER_CYCLING, system_select) == -1):
                print("error\n")

            time.sleep(WAITING_TIME)
            state_received = None
            while (state_received == None):
                state_received = bt_ser.readline()  #@andy: need to send a 0/1 for state and \n             
                success = bt_ser.readline()         # then send SUCCESS ACK

            if (success == SUCCESS_ACK):
                opower_state = state_received
            else:
                print("Incorrect message received from bluetooth")

        elif system_select == 'i':
            print("Toggling power on imaging system...\n")

            if (send_command(POWER_CYCLING, system_select) == -1):
                print("error\n")

            time.sleep(WAITING_TIME)
            state_received = None
            while (state_received == None):
                state_received = bt_ser.readline()  #@andy: need to send a 0/1 for state and \n             
                success = bt_ser.readline()         # then send SUCCESS ACK

            if (success == SUCCESS_ACK):
                ipower_state = state_received
            else:
                print("Incorrect message received from bluetooth")            
        
        print("Orientation system powered? = " + str(opower_state))
        print("Imaging system powered? = " + str(ipower_state) + "\n\n")

##        time.sleep(1)
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
                coords = [pitch, yaw, roll]
##CAUTION: need to implement xyz_to_Orbital function here on coords
                ## and send orbital coords
                if (send_command(MANUAL, coords) == -1): 
                    print("error\n")
                
                time.sleep(WAITING_TIME)
                state_received = None
                while (state_received == None):
                    state_received = bt_ser.readline()  #@andy: need to send a 0/1 for state and \n             
                    success = bt_ser.readline()         # then send SUCCESS ACK

                if (success == SUCCESS_ACK):
                    print('Moving ...')
                    done = 1
                    print('done')
                else:
                    print("Failed to send move command")
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

    while (not (key == 'm')):
        print("Enter angle of right ascension: ")
        ra = raw_input()
        print("Enter angle of declination")
        dec = raw_input()

        if (ra == 'm' or dec == 'm'):
                break
        else:
            ##format into coords to send here
            destination = [int(ra), int(dec)]  
            ##send
            send_command(NAVIGATE_TO, destination)

    
def save_image():
    send_command(SAVE, 'x')
    print("Capturing image...\n")

    #wait for and receive iamge save ACKnowledgement
    while (not bt_ser.readline()):
        pass
    
    print("Mission successful = " + bt_ser.readline())
    

'''*********************************************'''        
'''              INITIALISATIONS                '''
'''*********************************************'''
#configure serial connection
#consider replacing COM3 with a str variable \

cp2102_ser = serial.Serial(
    port=usbTTL_COM,\
    baudrate=COMS_BAUD,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=0)              #computer to CP2102 serial port, used for interfacing with the DSN block 10sec delay

#may need to initialize settings in AT mode here (see todo 2.1 and then send AT+RESET
#to enter pairing mode... or would this algorithm be used on board...
bt_ser = serial.Serial( #used for testing right now
    port=bluetooth_COM,\
    baudrate=COMS_BAUD,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=0)              #Bluetooth to computer serial port connection, used to transmit and receieve commands from the telescope

if ((cp2102_ser.isOpen()) and (bt_ser.isOpen())):
                
    print("Computer CP2102 connected to: " + cp2102_ser.portstr + ", baudrate: " + str(cp2102_ser.baudrate))
    print("Bluetooth " + bt_device + " connected to: " + bt_ser.portstr + ", baudrate: " + str(bt_ser.baudrate))
else:
    print("Failed to open a serial port")

###the code to configure settings would have to be on the micro on board (@Andy)
##if (bt_device == "HC06"):
##    cp2102_ser.writelines("AT")
##    if (cp2102_ser.readlines("OK")):
##        #proceed with next step of configuration
##        cp2102_ser.writelines("AT+NAME=METR4810\r\n")
##    else:
##        #check again
##        cp2102_ser.writelines("AT")
##        if (cp2102_ser.readlines("OK"):
##        #proceed with next step of configuration
##
##        else:
##            print("error, can't connect to " + bt_device)
##            

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
                4. Navigate to point \n\
                5. Shutdown")

        state = int(raw_input())
    
    elif state == CALIBRATION:
        #enter Calibration mode
        print("Now in calibration mode: ")
        calibrate()

        time.sleep(1)

        data = bt_ser.readline()
        print("data received from bluetooth: " + data)
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
    elif state == SHUTDOWN:
        break
print("closing serial ports..")
cp2102_ser.close()
bt_ser.close()
