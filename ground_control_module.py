##METR4810:: THE JOHN TEBBUTT SPACE TELESCOPE
##GROUND_CONTROL_MODULE SOFTWARE
##30 Mar 2018
##Last rev: 290418
##Author: John Webster

'''TODO:
- work with Andy for the "@andy" comments
    note3 Andy: always send success_ACK first if command was successful, then data
    note4 Andy: Currently send 1st coordinate, uint16_t, space character " " and '\n', and then second coord (RA, DEC)
- implement send_command() for all modes of operation
    E. - calibration
    C. - navigate to
- # read coordinates returned, in manual steer and nav_to
- ensure all error handling is taken care of such that no disconnection can occur
- design getCommandAndValue to work for each one of my functions on ground
- could implement a check statement on pyserial.write() statements (ret num of bytes written) to ensure
    that bytes written == len(data_sent)
- CAUTION: BE aware that when operating in reality, the command to be sent will be sent imiediately
    upon receive from DSN block, which means no delay in receiving from cp2102 and sending to scope, and
    could receive immediately back. Just check delays and handle read/write buffers appropriately
- implement for all 'send_commands'
    if not sendCommand():
        error;
    continue
- changed all ACKs and recvd to initialise as = "", and while ack == "" instead of None
        - realized that serial.readline() would return an empty string and make the variable not == None
TROUBLESHOOTING:
1. if the initial connection doesn't work to connect to Scope Blutooth, try again.
2. If "" recvd from DSN, and it freezes in sending... Swap the CP2102 COM ports

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
scope_COM = 'COM14'

#dsn_test variables
DSN_TEST_CHAR = '1'

#communication variables
COMS_BAUD = 1200 #set baudrate of communication between all devices # limited by DSN
DSN_COM = 'COM3'
bluetooth_COM = 'COM5'
bt_device = "HC06"
SUCCESS_ACK = 1 # NEED TO ESTABLISH AN ACK for success or failure
SERIAL_TXRX_WAIT = 0.5  # 500ms delay sending/reading serial
DSN_DELAY = 1
RX_TIMEOUT = 9999

#navigation variables
DEGREE_RESOLUTION = 16

#STATES
MENU =          0
CALIBRATION =   1
POWER_CYCLING = 2
MANUAL =        3
NAVIGATE_TO =   4
SAVE =          5
TEST_DSN =      6
SHUTDOWN =      7

state = 0

##calibration variables
CALIBRATE_ROLL = 'F' #commands telescope to steer YawRight and measure angle to correct the roll
#- or if it doesn't, it waits for an angle to roll sent by user at ground
CALIBRATE_PITCH = 'G' #scope moves up to lcoking point then steers back down to 0deg pitch 
CALIBRATE_YAW = 'H'  #scope rotates 360deg to calibrate MAG3110 magnetometer

##steering variables
counter = 0

##power cycle variables
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
    if ((DSN_SERIAL.isOpen()) and (BT_SERIAL.isOpen())):
        
        if (mode == CALIBRATION):        
            #send the same command that fnc was passed
            DSN_SERIAL.writelines(str(command))
            time.sleep(SERIAL_TXRX_WAIT)
            data_to_send = ""

            if TESTING:
                print("sending to DSN...")
                time.sleep(DSN_DELAY) 
            while data_to_send == "":
                data_to_send = DSN_SERIAL.readline()
                time.sleep(SERIAL_TXRX_WAIT)
##            print("sending to DSN...")
##            time.sleep(DSN_DELAY) 
##            data_to_send = DSN_SERIAL.readline()
##            time.sleep(SERIAL_TXRX_WAIT)

            print(data_to_send + " received from DSN, sending...")
            BT_SERIAL.writelines(data_to_send)
            time.sleep(SERIAL_TXRX_WAIT)
            ret_val = 1
            
        elif (mode == POWER_CYCLING or mode == SAVE): 
            #send the same command that fnc was passed
            DSN_SERIAL.writelines(str(command))
            time.sleep(SERIAL_TXRX_WAIT)
            data_to_send = ""

            if TESTING:
                print("sending to DSN...")
                time.sleep(DSN_DELAY) 
            while data_to_send == "":
                data_to_send = DSN_SERIAL.readline()
                time.sleep(SERIAL_TXRX_WAIT)

            #send data that was received back through cp2102
            print(data_to_send + " sent and received from DSN, sending...")
            BT_SERIAL.writelines(data_to_send)
            time.sleep(SERIAL_TXRX_WAIT)
            ret_val = 1

        elif ((mode == MANUAL) or (mode == NAVIGATE_TO)):
            print(str(command[0]) + str(command[1]))
            print("Steering to coords [" + str(command[0]) + ","\
                  + str(command[1]) + "]...")
            
            # should move this formatting to the function for better readability
            formatted_coords = convert_to_uint16_coords(userRA = command[0], userDEC = command[1])

            #rotate about z-axis userRA degrees - follow right-hand rule for direction
            DSN_SERIAL.writelines('z' + str(formatted_coords[0])) #ends with '\n'
            time.sleep(SERIAL_TXRX_WAIT)

            #rotate about y-axis userDEC degrees
            DSN_SERIAL.writelines('y' + str(formatted_coords[1]))

##              Ensure 0deg roll is maintained
##            DSN_SERIAL.writelines('x' + str(formatted_coords[0]))
            time.sleep(SERIAL_TXRX_WAIT)
            data_to_send = ""
            
            print("waiting...")
            time.sleep(DSN_DELAY) #could remove

            bit = DSN_SERIAL.read()
            rx_data = bit
            # CAUTION: need to read twice
            while(not (bit == "\n")):
                bit = DSN_SERIAL.read()
                rx_data = rx_data + str(bit)

            bit2 = DSN_SERIAL.read()
            rx_data2 = bit2
            while(not (bit2 == "\n")):
                bit2 = DSN_SERIAL.read()
                rx_data2 = rx_data2 + str(bit2)

            #send data that was received
            print(str(rx_data) + ',' + str(rx_data2) + " received from DSN, sending...")
##            BT_SERIAL.writelines(data_to_send)
            BT_SERIAL.writelines(rx_data)
            BT_SERIAL.writelines(rx_data2)
            time.sleep(SERIAL_TXRX_WAIT)
            ret_val = 1

        elif (mode == TEST_DSN):
            recvd = ""
            #global TESTING
        ##    if TESTING:
        ##        device = telescope #could be adapted for global use
        ##    else:
            device = DSN_SERIAL # unnecessary...
            
            print("sending test char to DSN...")
            global DSN_TEST_CHAR
            time1 = time.time()
            DSN_SERIAL.writelines(DSN_TEST_CHAR)
            print('sent ' + DSN_TEST_CHAR)
            print('waiting...')
            time.sleep(SERIAL_TXRX_WAIT)

            while recvd == "":
                recvd = device.readline()
                time2 = time.time()
            print("Received from DSN: " + recvd + ' after ' + str((time2-time1)) + ' seconds.\n')
            retval = 1
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
This function checks for a received ACK from telescope with a prescribed timeout
'''
def check_ACK():
    ack = ""
    a=0
##    BT_SERIAL.read() #CAUTION; EXTRA
    while (ack == "" and a < RX_TIMEOUT):
        ack = BT_SERIAL.read()
        a = a + 1

    if (a > RX_TIMEOUT):
        print ("timeout error; a = " + str(a))

    if (not (ack == '')):    
        if (ack == str(SUCCESS_ACK)):
            if TESTING:
                print("ACK received by ground control.\n")
        else:
            print("WHAT ack is this?: " + ack)
        return 1
    else:
        print('NACK received')
        return 0
    
'''
THIS FUNCTION SIMULATES A RESPONSE FROM THE TELESCOPE
'''
def telescope_sim_response(mode, system_select = 0):
    if ((telescope.isOpen()) and (BT_SERIAL.isOpen())):
        bit = telescope.read()
        rx_data = bit
        while(not (bit == "") or not (bit == '\n')):
            bit = telescope.read()
            rx_data = rx_data + str(bit)

        time.sleep(SERIAL_TXRX_WAIT)
        print("telescope received: " + str(rx_data))

        telescope.writelines(str(SUCCESS_ACK)) 
        print("SCOPE sent ack")
            
        if mode == POWER_CYCLING:
            global opower_state
            global ipower_state
            if system_select == 'p':
                telescope.writelines(str(1))
            elif system_select == 'o':
                opower_state = 1 - opower_state
                telescope.writelines(str(opower_state))
            elif system_select == 'i':
                ipower_state = 1 - ipower_state
                telescope.writelines(str(ipower_state))
    
        elif (mode == MANUAL) or (mode == NAVIGATE_TO):
            print('expect to receive current coordinates from scope')
            #read and send back first sent coordinate here:
            telescope.writelines(str(rx_data))
            time.sleep(SERIAL_TXRX_WAIT)
            print("sent " + str(rx_data))
            #read and send back second sent coordinate here:
            
            bit = telescope.read()
            rx_data = bit
            while(not (bit == '\n' or bit == "")): #CAUTION: TEST; may have to swtich back to not a and not b
                bit = telescope.read()
                rx_data = rx_data + str(bit)

            telescope.writelines(str(rx_data))
            time.sleep(SERIAL_TXRX_WAIT)
            print("sent " + str(rx_data))
##        telescope.writelines(str(rx_data))
##        print("sent rx_data")

'''
THIS FUNCTION OPTIONALLY PROMPTS USER FOR COORDS OR TAKES IN DEGREE VALUES
AND CONVERTS THEM TO A FORMATTED uint16 TO SEND to TELESCOPE FOR NAVIGATION
'''
def convert_to_uint16_coords(userRA = 0, userDEC = 0):
    if (userRA == 0 and (userDEC == 0)):
        print('Please enter angle of right ascension in degrees (RA): ')
        userRA = raw_input()

        print('Please enter angle of declination in degrees (DEC): ')
        userDEC = raw_input()
    
    convertedRA = np.uint16(deg_to_16bit(userRA))
    convertedDEC = np.uint16(deg_to_16bit(userDEC))
        
    '''
    optional: convert hrs:min:sec to decimal:
    A = (hours * 15) + (minutes * 0.25) + (seconds * 0.004166)
    B = ( ABS(Dec_degrees) + (Dec_minutes / 60) + (Dec_seconds / 3600)) * SIGN(Dec_Degrees)
    '''

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

'''
FUNCTION FOR CALIBRATING THE TELESCOPE'S ORIENTATION SYSTEM
'''
def calibrate():
    print("Select an axis to calibrate ('e' to exit): \n\
            1. Roll \n\
            2. Pitch \n\
            3. Yaw")
    axis_select = raw_input()

    while (not(axis_select == 'e')):
        if axis_select == '1': #calibrate roll
            print('Calibrating roll...')
            doneRoll = 0
            while (not doneRoll):
                send_command(CALIBRATION, CALIBRATE_ROLL)
                '''
                    response of telescope will either autonomously move yaw right and
                    measure angle to roll, OR user will have to trace the path of motion
                    and calculate the angle of correction manually and enter it here
                '''
                print('Telescope moved yaw [right]; enter roll correction angle (clockwise):')
                # use image feed to see if roll needs correction
                rollCorrection = raw_input()

                if rollCorrection == "":
                    rollCorrection = 0;

                print('Correct roll by ' + str(rollCorrection) + ' degrees? (y/n)' )

                decision = raw_input()

                while (not(decision == 'y') and not(decision == 'n')):
                    print("invalid input")
                    decision = raw_input()

                if (decision == 'y'):
                    send_command(CALIBRATION, rollCorrection) # scope sends ACK when successful
                    doneRoll = 1

                    if (not check_ACK()):
                        print ('error - no ack. returning to main menu')
                        break
                    else:
                        print('Calibrated Roll')
                else: #'n'
                    print('please reenter roll correction...')
        elif axis_select == '2': # calibrate pitch
            # Spacecraft should pitch up to gimbal lock, then move down automatically
            # to 0deg pitch
            print('Calibrating pitch...')
            donePitch = 0
            while (not donePitch):
                send_command(CALIBRATION, CALIBRATE_PITCH) #move up then come down to 0
                print('Telescope steering to vertical... \n\r Calibrating pitch...')
                print('Adjust pitch? (type j/k to inc/dec degree value or enter if ok)')

                #use image feed to determine if pitch correction is needed
                key = raw_input()
                adjustPitch = 0
                done = 0
                while (not(done)):
                    if (key == 'j'):
                        adjustPitch = adjustPitch + 1
                    elif (key == 'k'):
                        adjustPitch = adjustPitch - 1

                    print('adjustPitch (deg): ' + str(adjustPitch))
                    key = raw_input()
                    if (key == ""):
                        done = 1
                        print('\nSteer pitch ' + str(adjustPitch) + " degrees? (y/n to confirm)")

                        decision = 0

                        while (not(decision == 'y') and not(decision == 'n')):
                            decision = raw_input()

                        if (decision == 'y'):
                            send_command(CALIBRATION, adjustPitch) #adjustPitch value will be 0 if good
                              # scope sends ACK when successful
                            if (not check_ACK()):
                                print ('error - no ack. returning to main menu')
                                break
                            else: #recvd ack
                                print('Calibrated pitch\n\r Happy? (y/n)')
                                ans = 0
                                while (not(ans == 'y') and not(ans == 'n')):
                                    ans = raw_input()

                                if (ans == 'y'):
                                    donePitch = 1
                                    print("Done calibrating Pitch")
                                else:
                                    print ("Retrying pitch calibration...")
                        else:
                            print ("retry entry or 'e' to exit")
                        
                    elif (key == 'e'):
                        break
                      
        elif axis_select == '3': # calibrate yaw
            #spins 360deg to calibrate MAG3110 and then uses N heading to point
            #at 0deg relative to Hawken Gallery
            print('Calibrating yaw...')
            doneYaw = 0
            while (not doneYaw):
                send_command(CALIBRATION, CALIBRATE_YAW) #commands scope to spin 360 to calibrate mag3110
                #scope should automatically steer to 0deg in Hawken

                if (not check_ACK()):
                    print ('error - no ack. returning to main menu')
                    break
                else: #recvd ack
                    print('Calibrated yaw\n\r Happy? (y/n)')
                    ans = 0
                    while (not(ans == 'y') and not(ans == 'n')):
                        ans = raw_input()

                    if (ans == 'y'):
                        doneYaw = 1
                        print("Done calibrating Yaw")
                    else:
                        print ("Retrying yaw calibration...")
        print("Select an axis to calibrate ('e' to exit): \n\
                1. Roll \n\
                2. Pitch \n\
                3. Yaw")
        axis_select = raw_input()
  
    print("Finished calibration!")
    if TESTING: #clear buffer - maybe remove TESTING and always do this?
        rcvd = BT_SERIAL.readline()
        time.sleep(SERIAL_TXRX_WAIT)
        print("received:" + str(rcvd))

    global state
    state = 0
    return
##    print("Calibration mode\n")
##    #calibrate here...
####CAUTION: need to develop calibration algorithm
##    print("Enter a char to send: \n")
##    char_to_send = raw_input()
##
##    if (send_command(CALIBRATION, char_to_send)):
##        global finished
##        finished = 1
##    else:
##        return print("Error in sending command")
                                                          
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

##            time.sleep(SERIAL_TXRX_WAIT)

            ack = ""
            a=0
            while (ack == "" and a < RX_TIMEOUT):
                ack = BT_SERIAL.read()
                a = a + 1
            
            if (a > RX_TIMEOUT):
                print ("timeout error; a = " + str(a))

            print( "received data: " + str(ack))

            if (not (ack == '')):    
                if (ack == str(SUCCESS_ACK)):
                    print("All subsystems power cycled, success\n")
                    success = BT_SERIAL.readlines()
                    print("power cycle success: " + str(success))
                else:
                    print("Incorrect message received from bluetooth")
            else:
                print('NACK received')
        elif system_select == 'o': #TOGGLE ORIENTATION CONTROL POWER
            print("Toggling power on orientation control system...\n")

            if (send_command(POWER_CYCLING, system_select) == -1):
                print("error\n")

##            time.sleep(SERIAL_TXRX_WAIT)
            
            ack = ""
            a=0
            while (ack == "" and a < RX_TIMEOUT):
                ack = BT_SERIAL.read()
                a = a + 1

            if (a > RX_TIMEOUT):
                print ("timeout error; a = " + str(a))

            if (not (ack == '')):    
                if (ack == str(SUCCESS_ACK)):
                    print("Orientation control power cycled, success\n")
                    state_received = ""

                    while (state_received == ""):
                        state_received = BT_SERIAL.readlines()  #@andy: need to send a 0/1 for state and \n         

                    opower_state = state_received
                else:
                    print("Orientation system power did not send SUCCESS_ACK")
            else:
                print('NACK received')
                
        elif system_select == 'i': #TOGGLE IMAGING SUBSYSTEM POWER
            print("Toggling power on imaging system...\n")

            if (send_command(POWER_CYCLING, system_select) == -1):
                print("error\n")

##            time.sleep(SERIAL_TXRX_WAIT)
            
            ack = ""
            a=0
            while (ack == "" and a < RX_TIMEOUT):
                ack = BT_SERIAL.read()
                a = a + 1

            if (a > RX_TIMEOUT):
                print ("timeout error; a = " + str(a))

            if (not (ack == '')):    
                if (ack == str(SUCCESS_ACK)):
                    print("Imaging control power cycled, success\n")
                    state_received = ""

                    while (state_received == ""):
                        state_received = BT_SERIAL.readlines()  #@andy: need to send a 0/1 for state and \n         

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
should change to direct entry as delta, then send directly as delta+currentattitude
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

            while (not(decision == 'y') and not (decision == 'n')):
                decision = raw_input()

            if (decision == 'y'):
                #WAS REVERSED
                coords = [rightAsc, angleDec]

                if (send_command(MANUAL, coords) == -1): 
                    print("error\n")
                
                time.sleep(SERIAL_TXRX_WAIT)
                ack = ""
                a=0
                while (ack == "" and a < RX_TIMEOUT):
                    ack = BT_SERIAL.read()
                    a = a + 1

                if (a > RX_TIMEOUT):
                    print ("timeout error; a = " + str(a))

                if (not (ack == '')):    
                    if (ack == str(SUCCESS_ACK)):
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
                
'''                state_received = "" #moved from above last 'elif'
                while (state_received == ""):
                    state_received = BT_SERIAL.readline()  #@andy: need to send a 0/1 for state and \n             
                    success = BT_SERIAL.readline()         # then send SUCCESS ACK

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
            key = 'm'
        else:
            try:
                ra = int(ra)
            except ValueError:
                ra = 0

            try:
                dec = int(dec)
            except ValueError:
                dec = 0
                
            destination = [ra, dec]

            print('\nMove ' + "angleDec: " + str(dec) + " rightAsc: " + str(ra)\
                  + ' (deltas)? (y/n to confirm)')

            decision = 0

            while (not(decision == 'y') and not(decision == 'n')):
                decision = raw_input()

            if (decision == 'y'):
                if (send_command(NAVIGATE_TO, destination) == -1): 
                    print("error\n")
                
                ack = ""
                a=0
                while (ack == "" and a < RX_TIMEOUT):
                    ack = BT_SERIAL.read()
                    a = a + 1

                if (a > RX_TIMEOUT):
                    print ("timeout error; a = " + str(a))

                if (not (ack == '')):    
                    if (ack == str(SUCCESS_ACK)):


                        '''
                        #GET RECEIVED COORDINATES HERE

                        while (not (bit == " ")):
                            RxCoords = rcvdCoords + BT_SERIAL.read()
                        '''
                        
                        RxCoords = [0,0] # read coordinates returned, here

                        print("MOVED TO " + str(RxCoords[0]) + "," + str(RxCoords[1])+ " success\n")
                        #now read coords
                    else:
                        print("Incorrect message received from bluetooth")
                else:
                    print('NACK received')

                key = 'm' #signal done
                    
            elif (decision == 'n'):
                #retry entry
                print("Send a new move command: ")
                
'''
#THIS FUNCTION SENDS A COMMAND TO THE SCOPE TO SAVE AN IMAGE
'''
def save_image():
    print("Capturing image...\n")
    send_command(SAVE, 'x')

    #wait for and receive image save ACKnowledgement
    acked = ""
    while (acked == ""):
        acked = BT_SERIAL.readline()
    
    print("Mission successful = " + acked)
    
'''
SENDS A USER DEFINED CHAR TO DSN BLOCK AND WAITS FOR REPLY
PRINTS THE RECVD CHAR ONCE RECEIVED
'''
def DSN_test():
    global TESTING
    recvd = ""
##    if TESTING:
##        device = telescope #could be adapted for global use
##    else:
    device = DSN_SERIAL
    
    print("sending to DSN...")
    global DSN_TEST_CHAR
    DSN_SERIAL.writelines(DSN_TEST_CHAR)
    print('sent ' + DSN_TEST_CHAR)
    print('waiting...')
    time.sleep(SERIAL_TXRX_WAIT*2)

    while recvd == "":
        recvd = device.readline()
        
    print("Received from DSN: " + recvd + '\n')
    return recvd

'''*********************************************'''        
'''              INITIALISATIONS                '''
'''*********************************************'''
#configure serial connections
if TESTING:
    #this port is used to simulate the telescope
    telescope = serial.Serial(
        port=scope_COM,\
        baudrate=COMS_BAUD,\
        parity=serial.PARITY_NONE,\
        stopbits=serial.STOPBITS_ONE,\
        bytesize=serial.EIGHTBITS,\
            timeout=0)              #simulated telescope receiving/sending port (receieves BT_SERIAL.write)

#this port is used for communication with the DSN block before sending a command by BT
DSN_SERIAL = serial.Serial(
    port=DSN_COM,\
    baudrate=COMS_BAUD,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=0)              #computer to CP2102 serial port, used for interfacing with the DSN block 10sec delay

#this port is used to pair with the telescope and send commands via the laptop's built in BT
BT_SERIAL = serial.Serial( #used for testing right now
    port=bluetooth_COM,\
    baudrate=COMS_BAUD,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=0)              #Bluetooth to computer serial port connection, used to transmit and receieve commands from the telescope

if ((DSN_SERIAL.isOpen()) and (BT_SERIAL.isOpen())):
                
    print("Computer connected to DSN on port: " + DSN_SERIAL.portstr + ", baudrate: " + str(DSN_SERIAL.baudrate))
    print("Telescope " + bt_device + " connected to bluetooth via: " + BT_SERIAL.portstr + ", baudrate: " + str(BT_SERIAL.baudrate))
else:
    print("Failed to open a serial port")

###the code to configure settings would have to be on the micro on board (@Andy)
##if (bt_device == "HC06"):
##    DSN_SERIAL.writelines("AT")
##    if (DSN_SERIAL.readlines("OK")):
##        #proceed with next step of configuration
##        DSN_SERIAL.writelines("AT+NAME=METR4810\r\n")
##    else:
##        #check again
##        DSN_SERIAL.writelines("AT")
##        if (DSN_SERIAL.readlines("OK"):
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
                6. Save \n\
                7. DSN_test()")
        try:
            state = int(raw_input())
        except ValueError:
            state = MENU
            
    elif state == CALIBRATION:
        #enter Calibration mode
        calibrate()

        data = BT_SERIAL.readline()
        print("residual data received from telescope: " + data)
        state = MENU

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
    
    elif state == TEST_DSN:
        send_command(TEST_DSN)
        state = MENU
        
print("closing serial ports..")
DSN_SERIAL.close()
BT_SERIAL.close()
