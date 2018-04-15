##METR4810:: THE JOHN TEBBUTT SPACE TELESCOPE
##GROUND_CONTROL_MODULE SOFTWARE
##30 Mar 2018.
##Last rev: 130418
##Author: John Webster

'''TODO:
- NOTE: bluetooth com connection with HC06 doesn't always work right after a break in program
-test 'send-command' fnction - work with Andy for the "@andy" comments
    note3 Andy: always send success_ACK first if command was successful, then data
    note4 Andy: Currently send 1st coordinate, uint16_t, space character " ", and then second coord (RA, DEC)
- implement send_command() for all modes of operation
    E. - calibration
    C. - navigate to
- need to develop calibration algorithm with andy
- A. need to def coords_to_send() to format angle of declin. and ra to a two byte package to send
- # read coordinates returned, in manual steer and nav_to
- implement a method of handling a non integer entered for coordinates to send (i.e. go to 0,0 by default?
    - error occurs in line 481 destination = [,]
'''

from __future__ import print_function
import os
import numpy as np
##import cv2
import time
import serial

'''*********************************************'''        
'''              ^IMPORTS^                      '''
'''*********************************************'''

'''*********************************************'''        
'''              VARIABLE DECLARATIONS          '''
'''*********************************************'''
#testing variables:
TESTING = 1
bluetoothRX_Testing = 'COM4'

#communication variables
COMS_BAUD = 1200 #set baudrate of communication between all devices
usbTTL_COM = 'COM3'
bluetooth_COM = 'COM5'
bt_device = "HC06"
SUCCESS_ACK = 1 # NEED TO ASK ANDY WHAT CHAR HE WOULD LIKE TO SEND AS AN ACK for success or failure
WAITING_TIME = 1  # CAUTION: adjust waiting time as necessary during testing, or add a while loop
DSN_DELAY = 1
WAITING_TIMEOUT = 9999

#navigation variables
DEGREE_RESOLUTION = 16

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

'''
@brief  sends a command through the DSN block following protocol, 
        and then once it receives the command from the DSN block, it transmits 
        it through the bluetooth serial port
'''
def send_command(mode, command):
    ret_val = 0
    if ((cp2102_ser.isOpen()) and (bt_ser.isOpen())):
        
        if (mode == CALIBRATION or mode == POWER_CYCLING or mode == SAVE): 
            #send the same command that fnc was passed
            cp2102_ser.writelines(command)
            time.sleep(WAITING_TIME)
            data_to_send = None
            
            print("sending to DSN...")
            time.sleep(DSN_DELAY) 
            data_to_send = cp2102_ser.readline()
            time.sleep(WAITING_TIME)

            #send data that was received back through cp2102
            print(data_to_send + " received from DSN, sending...")
            bt_ser.writelines(data_to_send)
            time.sleep(WAITING_TIME)
            ret_val = 1

        elif ((mode == MANUAL) or (mode == NAVIGATE_TO)):
            print(str(command[0]) + str(command[1]))
            print("Steering to coords [" + str(command[0]) + ","\
                  + str(command[1]) + "]...")

            formatted_coords = coords_to_send(userRA = command[0], userDEC = command[1])
            cp2102_ser.writelines(str(formatted_coords[0]) + " ")
            cp2102_ser.writelines(str(formatted_coords[1]))
            time.sleep(WAITING_TIME)
            data_to_send = None
            
            print("waiting...")
            time.sleep(DSN_DELAY) #could remove

            bit = cp2102_ser.read()
            rx_data = bit
            # CAUTION: need to read twice
            while(not (bit == " ")):
                bit = cp2102_ser.read()
                rx_data = rx_data + str(bit)

            bit2 = cp2102_ser.read()
            rx_data2 = bit2
            while(not (bit2 == "")):
                bit2 = cp2102_ser.read()
                rx_data2 = rx_data2 + str(bit2)
##            #Need to test this more thoroughly
##            while (data_to_send == None):
##                data_to_send = cp2102_ser.readline()

            #send data that was received
            print(str(rx_data) + ',' + str(rx_data2) + " received from DSN, sending...")
##            bt_ser.writelines(data_to_send)
            bt_ser.writelines(rx_data)
            bt_ser.writelines(rx_data2)
            time.sleep(WAITING_TIME)
            ret_val = 1
            
        else:
            print("Invalid mode")
            ret_val = -1

        global TESTING
        if TESTING:
            if mode == POWER_CYCLING:
                telescope_sim_response(mode, system_select=command)
            else:
                telescope_sim_response(mode)
            print( "**SIMULATING SCOPE RESPONSE**")
        else:
            print('*not testing, waiting for response from telescope*')
        return ret_val
    else:
        print("error opening a serial port")
        return -1
    
'''
THIS FUNCTION SIMULATES A RESPONSE FROM THE TELESCOPE
'''
def telescope_sim_response(mode, system_select = 0):
    if ((telescope.isOpen()) and (bt_ser.isOpen())):
        bit = telescope.read()
        rx_data = bit
        while(not (bit == "")):
            bit = telescope.read()
            rx_data = rx_data + str(bit)
##        rx_data = telescope.readline()
##        rx_remainder = telescope.readline()
        time.sleep(WAITING_TIME)
        print("telescope received: " + str(rx_data))

        #send response from telescope
        telescope.writelines(str(SUCCESS_ACK))
        print("sent ack")
        
##        if (mode == CALIBRATION):
            
        if mode == POWER_CYCLING:
            global opower_state
            global ipower_state
            if system_select == 'p':
                telescope.writelines(str(1))
            elif system_select == 'o':
                opower_state = not opower_state
                telescope.writelines(str(opower_state))
            elif system_select == 'i':
                ipower_state = not ipower_state
                telescope.writelines(str(ipower_state))
    
        elif mode == MANUAL or mode == NAVIGATE_TO:
            print('expect to receive current coordinates from scope')
##        telescope.writelines(str(rx_data))
##        print("sent rx_data")

'''
THIS FUNCTION OPTIONALLY PROMPTS USER FOR COORDS OR TAKES IN DEGREE VALUES
AND CONVERTS THEM TO A FORMATTED BYTE TO SEND TELESCOPE
'''
def coords_to_send(userRA = 0, userDEC = 0):
    if (userRA == 0 and (userDEC == 0)):
        print('Please enter angle of right ascension in degrees (RA): ')
        userRA = raw_input()

        print('Please enter angle of declination in degrees (DEC): ')
        userDEC = raw_input()
    
    convertedRA = np.uint16(deg_to_16bit(userRA))
    convertedDEC = np.uint16(deg_to_16bit(userDEC))

    if TESTING:
        print ('converted ' + str(userRA) + ',' + str(userDEC) + ' to ' \
           + str(convertedRA) + ',' + str(convertedDEC) + '.')
        print('send now')
    coords = [convertedRA, convertedDEC]
    return coords

 
#CONVERTS DEGREES TO A SCALED VALUE FROM 0 TO 2^DEGREE_RESOLUTION

def deg_to_16bit(degrees):
    global DEGREE_RESOLUTION
    convertedVal = (2**DEGREE_RESOLUTION)/360 * degrees + (2**(DEGREE_RESOLUTION-1))
    print('degrees, convertedVal: ' + str(degrees) + ',' + str(convertedVal))
    return convertedVal


#THIS FUNCTION IS USED FOR CALIBRATING THE TELESCOPE'S ORIENTATION SYSTEM
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
                                                          
'''
#THIS FUNCTION IS USED FOR SELECTIVELY POWER CYCLING SUBSYSTEMS
'''
def power_cycle():
    global opower_state # get orientation power state here
    global ipower_state # get imaging power state here
    print("Select a system to power cycle (press 'm' to exit): \n\
                'p': Power on all subsystems \n\
                'o': Orientation control \n\
                'i': Imaging system \n ")
    system_select = raw_input()

    while (not(system_select == 'm')):

        if system_select == 'p': #POWER CYCLE ALL SUBSYSTEMS
            print("All systems will be rebooted now...")
            if (send_command(POWER_CYCLING, system_select) == -1):
                print("error\n")

##            time.sleep(WAITING_TIME)

            ack = None
            a=0
            while (ack == None and a < WAITING_TIMEOUT):
                ack = bt_ser.read()
                a = a + 1
            
            if (a > WAITING_TIMEOUT):
                print ("timeout error; a = " + str(a))

            print( "received data: " + str(ack))

            if (not (ack == '')):    
                if (int(ack) == SUCCESS_ACK):
                    print("All subsystems power cycled, success\n")
                    success = bt_ser.readlines()
                    print("power cycle success: " + str(success))
                else:
                    print("Incorrect message received from bluetooth")
            else:
                print('NACK received')
        elif system_select == 'o': #TOGGLE ORIENTATION CONTROL POWER
            print("Toggling power on orientation control system...\n")

            if (send_command(POWER_CYCLING, system_select) == -1):
                print("error\n")

##            time.sleep(WAITING_TIME)
            
            ack = None
            a=0
            while (ack == None and a < WAITING_TIMEOUT):
                ack = bt_ser.read()
                a = a + 1

            if (a > WAITING_TIMEOUT):
                print ("timeout error; a = " + str(a))

            if (not (ack == '')):    
                if (int(ack) == SUCCESS_ACK):
                    print("Orientation control power cycled, success\n")
                    state_received = None

                    while (state_received == None):
                        state_received = bt_ser.readlines()  #@andy: need to send a 0/1 for state and \n         

                    opower_state = state_received
                else:
                    print("Orientation system power did not send SUCCESS_ACK")
            else:
                print('NACK received')
                
        elif system_select == 'i': #TOGGLE IMAGING SUBSYSTEM POWER
            print("Toggling power on imaging system...\n")

            if (send_command(POWER_CYCLING, system_select) == -1):
                print("error\n")

##            time.sleep(WAITING_TIME)
            
            ack = None
            a=0
            while (ack == None and a < WAITING_TIMEOUT):
                ack = bt_ser.read()
                a = a + 1

            if (a > WAITING_TIMEOUT):
                print ("timeout error; a = " + str(a))

            if (not (ack == '')):    
                if (int(ack) == SUCCESS_ACK):
                    print("Imaging control power cycled, success\n")
                    state_received = None

                    while (state_received == None):
                        state_received = bt_ser.readlines()  #@andy: need to send a 0/1 for state and \n         

                    ipower_state = state_received
                else:
                    print("Imaging system power did not send SUCCESS_ACK")
            else:
                print('NACK receieved')
        
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
'''
#THIS FUNCTION IS USED FOR STEERING THE SCOPE MANUALLY
'''
def manual_steer():
    print("Steering mode (press 'm' to return to main menu):\n")
    key = 0
    #key = ord(getch())
    print(key)

    angleStep = 10
    angleDec = 0
    rightAsc = 0
    
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
            angleDec = angleDec + angleStep
        elif (key == 's'):
            angleDec = angleDec - angleStep
        elif (key == 'd'):
            rightAsc = rightAsc + angleStep
        elif (key == 'a'):
            rightAsc = rightAsc - angleStep
##        elif (key == 'e'):
##            roll = roll + angleStep
##        elif (key == 'q'):
##            roll = roll - angleStep
        elif (key == 'j'):         #else change angleStep size
            angleStep = angleStep / 2
        elif (key == 'k'):
            angleStep = angleStep * 2

        print("angleDec: " + str(angleDec) + " rightAsc: " + str(rightAsc)\
              + "\r")

        if (key == ""): 
            print('\nMove ' + "angleDec: " + str(angleDec) + " rightAsc: " + str(rightAsc)\
                  + ' (deltas)? (y/n to confirm)')

            decision = 0

            while (not(decision == 'y') or (decision == 'n')):
                decision = raw_input()

            if (decision == 'y'):
                coords = [angleDec, rightAsc]
##CAUTION: need to implement xyz_to_Orbital function here on coords
                ## and send orbital coords
                if (send_command(MANUAL, coords) == -1): 
                    print("error\n")
                
                time.sleep(WAITING_TIME)
                ack = None
                a=0
                while (ack == None and a < WAITING_TIMEOUT):
                    ack = bt_ser.read()
                    a = a + 1

                if (a > WAITING_TIMEOUT):
                    print ("timeout error; a = " + str(a))

                if (not (ack == '')):    
                    if (int(ack) == SUCCESS_ACK):
                        print("Manual steer successful\n")
                        return
                    else:
                        print("Manual steer did not rcv SUCCESS_ACK")
                        print("Returning to Menu")
                        global state
                        state = 0
                        return
                else:
                    print('nack recvd')
                    
            elif (decision == 'n'):
                #retry entry
                print("Send a new move command: ")
                
'''                state_received = None #moved from above last 'elif'
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
'''
'''             
#THIS FUNCTION TAKES A POLAR COORDINATE PAIR AND SENDS IT TO THE SCOPE
'''
def navigate_to():
    print("Navigate to point.....\n(press 'm' to return to main menu):\n")
    angleDec = 0
    rightAsc = 0
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
            destination = [int(ra), int(dec)]  
            if (send_command(NAVIGATE_TO, destination) == -1): 
                print("error\n")
            
            time.sleep(WAITING_TIME)
            ack = None
            a=0
            while (ack == None and a < WAITING_TIMEOUT):
                ack = bt_ser.read()
                a = a + 1

            if (a > WAITING_TIMEOUT):
                print ("timeout error; a = " + str(a))

            if (not (ack == '')):    
                if (int(ack) == SUCCESS_ACK):
                    coordinates = [0,0] # read coordinates returned, here

                    print("MOVED TO " + str(coordinates[0]) + ", success\n")
                    #now read coords
                else:
                    print("Incorrect message received from bluetooth")
            else:
                print('NACK received')

'''
#THIS FUNCTION SENDS A COMMAND TO THE SCOPE TO SAVE AN IMAGE
'''
def save_image():
    print("Capturing image...\n")
    send_command(SAVE, 'x')

    #wait for and receive image save ACKnowledgement
    acked = None
    while (acked == None):
        acked = bt_ser.readline()
    
    print("Mission successful = " + acked)
    

'''*********************************************'''        
'''              INITIALISATIONS                '''
'''*********************************************'''
#configure serial connections
if TESTING:
    #this port is used to simulate the telescope
    telescope = serial.Serial(
        port=bluetoothRX_Testing,\
        baudrate=COMS_BAUD,\
        parity=serial.PARITY_NONE,\
        stopbits=serial.STOPBITS_ONE,\
        bytesize=serial.EIGHTBITS,\
            timeout=0)              #simulated telescope receiving/sending port (receieves bt_ser.write)

#this port is used for communication with the DSN block before sending a command by BT
cp2102_ser = serial.Serial(
    port=usbTTL_COM,\
    baudrate=COMS_BAUD,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=0)              #computer to CP2102 serial port, used for interfacing with the DSN block 10sec delay

#this port is used to pair with the telescope and send commands via the laptop's built in BT
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
  
    if state == MENU:
        #display menu selection and instructions
        print("Menu select: \n\
                1. Calibration \n\
                2. Subsystem power management \n\
                3. Manual free steering \n\
                4. Navigate to point \n\
                5. Shutdown \n\
                6. Save")

        state = int(raw_input())
    
    elif state == CALIBRATION:
        #enter Calibration mode
        print("Now in calibration mode: ")
        calibrate()

        time.sleep(1)

        data = bt_ser.readline()
        print("data received from telescope: " + data)
        if finished:
            state = MENU
            print("done\n\n")
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
        navigate_to()
        time.sleep(1)
        state = MENU

        #exit when....
    elif state == SAVE:

        #need to implement a method of interrupting to save...
        if save_image():
            print ('image save successful')
        
        state = MENU
    elif state == SHUTDOWN:
        break
print("closing serial ports..")
cp2102_ser.close()
bt_ser.close()
