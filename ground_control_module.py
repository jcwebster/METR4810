##METR4810:: THE JOHN TEBBUTT SPACE TELESCOPE
##GROUND_CONTROL_MODULE SOFTWARE
##30 Mar 2018
##Last rev: 240518
##Author: John Webster

'''
TODO:
- *AFTER HC06 IS RESTARTED ON TELESCOPE,
    MUST READ BUFFER 2X TO CLEAR "+DISC:SUCCESS" AND "OK" MSGS on telescope
- fix use of parentheses in all while, if statements

STARTUP:
1. Start Windows and Liclipse, command prompt, or IDLE. Pair with the telescope HC06.
2. Plug in the DSN USB_TTL converter to a known COM port.
    2.1 If testing, plug in the second USB_TTL converter in a known scope_COM port
        on other PC
    2.2 If not testing, plug in DSN block using the DSN Cable
3. Run ground_control_module.py

TROUBLESHOOTING when testing:
1. If the initial connection doesn't work to connect to Scope Bluetooth, try again.
2. If "" recvd from DSN, and it freezes in sending... Swap the CP2102 COM ports
    or swap tx/rx (for HC06 and cp2102, rx-rx, tx-tx)
3. If HC06 is busy, close IDLE window and reopen.

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
#testing variables#
TESTING = 1
scope_COM = 'COM15'

#dsn_test variables#
DSN_TEST_CHAR = '1'

#communication variables#
COMS_BAUD = 1200 #set baudrate of communication between all devices; limited by DSN
DSN_COM = 'COM3'
bluetooth_COM = 'COM5'
bt_device = 'HC06'
SUCCESS_ACK = 1         #ACK to be received from telescope on successful operation
NULLCORRECTION = 'Z'
SERIAL_TXRX_WAIT = 0.5  #500ms delay sending/reading serial
BT_TXRX_WAIT = 0.5
DSN_DELAY = 1
RX_TIMEOUT = 99

if not TESTING:
    bluetooth_COM = 'COM10'

#navigation variables
DEGREE_RESOLUTION = 16
current_coords = [0, 0] #stored as RA, DEC

#STATES
MENU = 0
CALIBRATION = 1
POWER_CYCLING = 2
DELTA_STEER = 3
NAVIGATE_TO = 4
SAVE = 5
DSN_TEST_STATE = 6
SHUTDOWN = 7

state = 0

#calibration variables#
CALIBRATE_ROLL = 'F' #commands telescope to steer YawRight and measure angle to correct the roll
CALIBRATE_PITCH = 'G' #scope moves up to locking point then steers back down to 0deg pitch 
CALIBRATE_YAW = 'H'  #calibrate yaw with MAG3110 magnetometer

#steering variables#
counter = 0

#power cycle variables#
opower_state = 0
ipower_state = 0

'''*********************************************'''        
'''              FUNCTION DEFINITIONS           '''
'''*********************************************'''

def bootup():
    """Reads entire data buffer from Bluetooth device and prints the data"""
    a = 0
    data_stream = ""
    data2 = ""
    if BT_SERIAL.isOpen():
        while a < RX_TIMEOUT:
            data_stream = data_stream + BT_SERIAL.readline() + " "
            if TESTING:
                data2  = data2 + telescope.readline() + " "
            a = a + 1

        print(data_stream + data2)
    else:
        print("error: could not connect")
   
   
def send_command(mode, command):
    """Sends a command through the DSN block and then to telescope
     
    Formats data according to mode and sends a command through the DSN block 
    following protocol, and then once the command is received from the DSN block, 
    the data is transmitted via bluetooth to the telescope.
    
    Args:
        mode: specifies mode of operation of telescope
        command: data as relevant to the mode
    
    Returns:
        True if transmitted successfully, false otherwise.
    """
    ret_val = 0
    if DSN_SERIAL.isOpen() and BT_SERIAL.isOpen():

        if mode == DSN_TEST_STATE:
            test_DSN()
            ret_val = 1
            
        elif mode == POWER_CYCLING or mode == SAVE: 
            #send the same command that fnc was passed
            DSN_SERIAL.writelines(str(command))
            time.sleep(SERIAL_TXRX_WAIT)
            data_to_send = None
            
            print("sending to DSN...")
            time.sleep(DSN_DELAY) 
            data_to_send = DSN_SERIAL.readline()
            time.sleep(SERIAL_TXRX_WAIT)

            #send data that was received back through cp2102
            print(data_to_send + " received from DSN, sending...")
            BT_SERIAL.writelines(data_to_send)
            time.sleep(SERIAL_TXRX_WAIT)
            ret_val = 1
            
        elif mode == CALIBRATION:        
            #send the same command that fnc was passed
            DSN_SERIAL.writelines(str(command))
            time.sleep(SERIAL_TXRX_WAIT)
            data_to_send = None
            
            print("sending to DSN...")
            time.sleep(DSN_DELAY) 
            data_to_send = DSN_SERIAL.readline()
            time.sleep(SERIAL_TXRX_WAIT)

            #send data that was received back through cp2102
            print(data_to_send + " received from DSN, sending...")
            if data_to_send == '32768':
                if TESTING:
                    print('sending nullCorrection angle to scope')
                data_to_send = NULLCORRECTION
                
            BT_SERIAL.writelines(data_to_send)
            time.sleep(SERIAL_TXRX_WAIT)
            ret_val = 1
            
        elif mode == DELTA_STEER:
            global current_coords
            errorCorrected = 0
            
            #add delta command values to current coords
            current_coords[0] = current_coords[0] + command[0]
            current_coords[1] = current_coords[1] + command[1]
            while abs(current_coords[0]) > 180:
                print("input your desired RA within +/-180:")
                current_coords[0] = raw_input()

                try:
                    current_coords[0] = float(current_coords[0])
                except:
                    print("you must be trying to anger me... \r\n Setting RA to 0.")
                    current_coords[0] = 0
                errorCorrected = 1
                
            while abs(current_coords[1]) > 90:
                print("input your desired DEC within +/-90:")
                current_coords[1] = raw_input()

                try:
                    current_coords[1] = float(current_coords[1])
                except:
                    print("you must be trying to anger me... \r\n Setting DEC to 0.")
                    current_coords[1] = 0
                errorCorrected = 1
            
            #format and send new coords to navigate to
            formatted_coords = convertToUint16Coords(userRA = current_coords[0], userDEC = current_coords[1])

            #rotate about z-axis userRA degrees - follow right-hand rule for direction
            DSN_SERIAL.writelines(str(formatted_coords[0]) + '\n')
            time.sleep(SERIAL_TXRX_WAIT)

            #rotate about y-axis userDEC degrees
            DSN_SERIAL.writelines(str(formatted_coords[1]))

            time.sleep(SERIAL_TXRX_WAIT)
            data_to_send = None
            
            print("waiting...")
            time.sleep(DSN_DELAY) #could remove

            bit = DSN_SERIAL.read()
            rx_data = bit
            while not (bit == "\n") and not (bit == ""):
                bit = DSN_SERIAL.read()
                rx_data = rx_data + str(bit)

            bit2 = DSN_SERIAL.read()
            rx_data2 = bit2
            while not (bit2 == "\n") and not (bit2 == ""):
                bit2 = DSN_SERIAL.read()
                rx_data2 = rx_data2 + str(bit2)

            print(str(rx_data) + ',' + str(rx_data2) + " received from DSN, sending...")

            try:
                current_coords[0] = int(rx_data)
            except ValueError:
                print("ERROR: couldn't convert int angle RA from DSN")
                current_coords[0] = command[0] ## assume near this value
                
            try:
                current_coords[1] = int(rx_data2)
            except ValueError:
                print("ERROR: couldn't convert int angle DEC from DSN")
                current_coords[1] = command[1] # assume near this value
                
            BT_SERIAL.writelines('z' + rx_data)
            BT_SERIAL.writelines('y' + rx_data2)
            time.sleep(SERIAL_TXRX_WAIT)
            ret_val = 1
            
        elif mode == NAVIGATE_TO:
            global current_coords
    
            print("Steering to coords [" + str(command[0]) + ","\
                  + str(command[1]) + "]...")

            formatted_coords = convertToUint16Coords(userRA = command[0], userDEC = command[1])

            #rotate about z-axis userRA degrees - follow right-hand rule for direction
            DSN_SERIAL.writelines(str(formatted_coords[0]) + '\n') 
            time.sleep(SERIAL_TXRX_WAIT)

            #rotate about y-axis userDEC degrees
            DSN_SERIAL.writelines(str(formatted_coords[1]))
            time.sleep(SERIAL_TXRX_WAIT)
            data_to_send = None
            
            print("waiting...")
            time.sleep(DSN_DELAY)

            bit = DSN_SERIAL.read()
            rx_data = bit
            while not (bit == "\n") and not (bit == ""):
                bit = DSN_SERIAL.read()
                rx_data = rx_data + str(bit)

            bit2 = DSN_SERIAL.read()
            rx_data2 = bit2
            while not (bit2 == "\n") and not (bit2 == ""):
                bit2 = DSN_SERIAL.read()
                rx_data2 = rx_data2 + str(bit2)

            #send data that was received
            print(str(rx_data) + ',' + str(rx_data2) + " received from DSN, sending...")
            try:
                current_coords[0] = int(rx_data)
            except ValueError:
                print("ERROR: couldn't get angle RA")
                current_coords[0] = command[0] ## assume near this value
                
            try:
                current_coords[1] = int(rx_data2)
            except ValueError:
                print("ERROR: couldn't get angle DEC")
                current_coords[1] = command[1] ## assume near this value
                
            BT_SERIAL.writelines('z' + rx_data)
            BT_SERIAL.writelines('y' + rx_data2)
            time.sleep(SERIAL_TXRX_WAIT)
            ret_val = 1
            
        else:
            print("Invalid mode")
            ret_val = -1

        global TESTING
        if TESTING:
            print( "**SIMULATING SCOPE RESPONSE**")

            if mode == POWER_CYCLING:
                telescope_sim_response(mode, system_select=command)
            elif mode == CALIBRATION:
                telescope_sim_response(SUCCESS_ACK)
            else:
                telescope_sim_response(mode)
        else:
            print('*not testing, waiting for response from telescope*')
        return ret_val
    
    else:
        print("ERROR: error opening a serial port")
        return -1


def check_ACK():
    """Checks for a received ACK from telescope with a prescribed timeout
    
    Args:
        none
        
    Returns:
        1 on success, 0 if NACK
    """
    ack = None
    a = 0
    while ack == None and a < RX_TIMEOUT:
        ack = BT_SERIAL.read()
        a = a + 1

    if a > RX_TIMEOUT:
        print("ERROR: timeout error; a = " + str(a))
        return 0

    if not (ack == ''):    
        if ack == str(SUCCESS_ACK):
            if TESTING:
                print("ACK received.\n")
            return 1
        else:
            print("ERROR: improper ack received: " + ack) 
            return 0
    else:
        print('ERROR: NACK received')
        return 0
    

def telescope_sim_response(mode, system_select = 0):
    """Simulates the telescope response
    
    Called if the TESTING variable is defined.
    
    Args: 
        mode: specifies which mode the telescope is in
        system_select: data pertaining to the mode of operation
    
    Returns:
        Sends an ACK or coordinates as required by the mode of operation.
    """
    if telescope.isOpen() and BT_SERIAL.isOpen():
        bit = telescope.read()
        rx_data = bit
        while not (bit == "") and not (bit == '\n'):
            bit = telescope.read()
            rx_data = rx_data + str(bit)

        time.sleep(SERIAL_TXRX_WAIT)
        print("telescope received: " + str(rx_data))

        if mode == SUCCESS_ACK:
            telescope.writelines(str(mode)) 
            print("sent ack")
        elif not (mode == CALIBRATION):
            #send default response from telescope
            telescope.writelines(str(SUCCESS_ACK))
            
        if mode == POWER_CYCLING:
            global opower_state
            global ipower_state
            if system_select == 'p':
                telescope.writelines('1')
            elif system_select == 'o':
                try:            
                    opower_state = int(opower_state)
                except ValueError:
                    opower_state = 0

                opower_state = 1 - opower_state
                telescope.writelines(str(opower_state))
            elif system_select == 'i':
                try:            
                    ipower_state = int(ipower_state)
                except ValueError:
                    ipower_state = 0

                ipower_state = 1 - ipower_state
                telescope.writelines(str(ipower_state))
            elif system_select == 't':
                tpower_state = 1 

        elif mode == DELTA_STEER or mode == NAVIGATE_TO:
            bit = telescope.read()
            rx_data2 = bit
            while not(bit == "") and not (bit == '\n'):
                bit = telescope.read()
                rx_data2 = rx_data2 + str(bit)
            print("and " + str(rx_data2))

            print('expect to receive current coordinates from scope')
            #**read and send back angle RA coordinate here:
            telescope.writelines(str(40960) + "\n")
            time.sleep(SERIAL_TXRX_WAIT)
            print("sent 40960 (45) in place of:" + str(rx_data))

            #**send back angle DEC coordinate here:
            telescope.writelines(str(38229))
            time.sleep(SERIAL_TXRX_WAIT)
            print("sent 38229 (30) in place of: " + str(rx_data2))


def convertToUint16Coords(userRA = 0, userDEC = 0):
    """Converts float coordinates to uint16 encoded value for MSP430 onboard
    
    Prompts user for coords if not provided and converts a float coordinate pair 
    right ascension, declination to uint16 encoded value from -180 to 180
    
    Args:
        userRA: angle of right ascension provided by user
        userDEC: angle of declination provided by user
    Returns:
        coords[ra, dec]: a list coordinate pair of right ascension, declination, 
                        encoded as a uint16 value
    """ 
    if userRA == 0 and userDEC == 0:
        print('Please enter angle of right ascension in degrees (RA): ')
        userRA = raw_input()
        try:
            userRA = float(userRA)
        except ValueError:
            userRA = 0;
            print("ERROR: not a valid number")
        print('Please enter angle of declination in degrees (DEC): ')
        userDEC = raw_input()
        try:
            userDEC = float(userDEC)
        except ValueError:
            userDEC = 0;
            print("ERROR: not a valid number")

    convertedRA = np.uint16(deg_to_16bit(userRA))
    convertedDEC = np.uint16(deg_to_16bit(userDEC))
            
    '''
    #optional: convert hrs:min:sec to decimal:
    A = (hours * 15) + (minutes * 0.25) + (seconds * 0.004166)
    B = ( ABS(Dec_degrees) + (Dec_minutes / 60) + (Dec_seconds / 3600)) * SIGN(Dec_Degrees)
    '''

    if TESTING:
        print ('converted ' + str(userRA) + ',' + str(userDEC) + ' to ' \
           + str(convertedRA) + ',' + str(convertedDEC) + '.')
        print('send now')

    coords = [convertedRA, convertedDEC]
    return coords


def deg_to_16bit(degrees):
    """Converts float coordinates to uint16 encoded value representing -180 to 180
    
    Args:
        degrees: a float degree value to be encoded
    
    Returns:
        convertedVal: from 0 to 2^16 representing -180 to 180.
    """
    global DEGREE_RESOLUTION
    convertedVal = 32768 

    if abs(degrees) > 180:
        print("ERROR: Degree value must be within +/- 180 degrees or within +/-90 for declination.")
 
    convertedVal = int((2**DEGREE_RESOLUTION)/360 * degrees + (2**(DEGREE_RESOLUTION-1)))
    
    if TESTING:
        print('degrees, convertedVal: ' + str(degrees) + '-> ' + str(convertedVal))

    return convertedVal


def uint16_to_deg(uint16Value):
    """Converts a uint16 encoded degree value to a float value
    
    Args:
        uint16Value: the encoded degree value
    
    Returns:
        convertedDegrees: float value degrees
    """
    global DEGREE_RESOLUTION
    convertedDegrees = (uint16Value - 2**(DEGREE_RESOLUTION-1)) * 360 / float(2**DEGREE_RESOLUTION)
    
    if TESTING:
        print('degrees, convertedVal: ' + str(convertedDegrees) + '<-' + str(uint16Value))
    return convertedDegrees


def calibrate():
    """Calibrates the telescope's 3 axes"""
    print("Select an axis to calibrate ('e' to exit): \n\
            1. Roll \n\
            2. Pitch \n\
            3. Yaw")
    axis_select = raw_input()

    while not(axis_select == 'e'):
        if axis_select == '1': #calibrate roll
            print('Calibrating roll...')
            doneRoll = 0

            print("Telescope moving yaw right in 10...")
            send_command(CALIBRATION, CALIBRATE_ROLL)
            time.sleep(BT_TXRX_WAIT)
            if not check_ACK():
                print ('ERROR:  - no ack. Returning to main menu.')
                return
            
            while not doneRoll:
                '''
                    response of telescope will either autonomously move yaw right and
                    measure angle to roll, OR user will have to trace the path of motion
                    and calculate the angle of correction manually and enter it here
                '''
                print('Enter roll correction angle (clockwise):')
                rollCorrection = raw_input()

                if rollCorrection == "":
                    rollCorrection = 0;

                print('Correct roll by ' + str(rollCorrection) + ' degrees? (y/n)' )

                try:
                    rollCorrection = float(rollCorrection)
                except ValueError:
                    rollCorrection = 0;
                    print("ERROR: invalid roll adjust angle")

                decision = raw_input()

                while not(decision == 'y') and not(decision == 'n'):
                    print("ERROR: invalid input")
                    decision = raw_input()

                if decision == 'y':
                    #encode rollCorrection
                    rollCorrection = deg_to_16bit(rollCorrection)
                    send_command(CALIBRATION, rollCorrection) #expect ACK if success
                    time.sleep(BT_TXRX_WAIT)

                    doneRoll = 1

                    if not check_ACK():
                        print ('error - no ack. Returning to main menu.')
                        return
                    else:
                        print('Calibrated Roll')
                else: #'n'
                    print('please reenter roll correction...')
        elif axis_select == '2': # calibrate pitch
            # Spacecraft should pitch up to gimbal lock, then move down automatically
            # to 0deg pitch
            print('Calibrating pitch...')

            donePitch = 0

            print('Telescope steering to vertical... \n\r ')
            send_command(CALIBRATION, CALIBRATE_PITCH) #move up then come down to 0
            time.sleep(BT_TXRX_WAIT)
            if not check_ACK():
                print ('ERROR:  - no ack. Returning to main menu.')
                return
            
            while not donePitch:
                print('Adjust pitch? (type degree value or enter if ok)')

                adjustPitch = raw_input()

                if adjustPitch == "":
                    adjustPitch = 0;

                print('Correct pitch by ' + str(adjustPitch) + ' degrees? (y/n)' )

                try:
                    adjustPitch = float(adjustPitch)
                except ValueError:
                    adjustPitch = 0;
                    print("invalid pitch adjust angle")

                decision = raw_input()

                while not(decision == 'y') and not(decision == 'n'):
                    print("invalid input")
                    decision = raw_input()

                if (decision == 'y'):
                    #encode adjustPitch
                    adjustPitch = deg_to_16bit(adjustPitch)
                    send_command(CALIBRATION, adjustPitch) # scope sends ACK when successful
                    time.sleep(BT_TXRX_WAIT)

                    donePitch = 1

                    if not check_ACK():
                        print ('error - no ack. Returning to main menu.')
                        return
                    else:
                        print('Calibrated pitch.')
                else: #'n'
                    print('please reenter pitch correction...')
        elif axis_select == '3': # calibrate yaw
            #spins 360deg to calibrate MAG3110 and then uses N heading to point
            #at 0deg relative to Hawken Gallery
            print('Calibrating yaw...')
            doneYaw = 0

            send_command(CALIBRATION, CALIBRATE_YAW)
            time.sleep(BT_TXRX_WAIT)
            if not check_ACK():
                print ('ERROR:  - no ack. Returning to main menu.')
                return

            while not doneYaw:
                print('Adjust yaw? (clockwise):')
                yawCorrection = raw_input()

                if yawCorrection == "":
                    yawCorrection = 0;

                print('Correct yaw by ' + str(yawCorrection) + ' degrees? (y/n)' )

                try:
                    yawCorrection = float(yawCorrection)
                except ValueError:
                    yawCorrection = 0;
                    print("invalid yaw adjust angle")

                decision = raw_input()

                while not(decision == 'y') and not(decision == 'n'):
                    print("invalid input")
                    decision = raw_input()

                if decision == 'y':

                    #encode yawCorrection
                    yawCorrection = deg_to_16bit(yawCorrection)
                    send_command(CALIBRATION, yawCorrection) # expect ACK on success
                    time.sleep(BT_TXRX_WAIT)

                    doneYaw = 1

                    if not check_ACK():
                        print ('error - no ack. Returning to main menu.')
                        return
                    else:
                        print('Calibrated Yaw')
                else: #'n'
                    print('please reenter yaw correction...')
                    
        print("Select an axis to calibrate ('e' to exit): \n\
                1. Roll \n\
                2. Pitch \n\
                3. Yaw")
        axis_select = raw_input()
    
    print("Finished calibration!")
    
    if TESTING: #clear buffer - maybe remove TESTING and always do this?
        rcvd = BT_SERIAL.readline()
        time.sleep(BT_TXRX_WAIT)
        print("received:" + str(rcvd))
    global state
    state = 0
    return

                                                          
def power_cycle():
    """Function to control states of individual power systems onboard"""
    global opower_state 
    global ipower_state
    print("Select a system to power cycle (press 'e' to exit): \n\
                'p': Toggle power of all subsystems \n\
                'o': Orientation control \n\
                'i': Imaging system \n\
                't': Telemetry system \n\
                'm': reset microcontroller")
    system_select = raw_input()

    while not(system_select == 'e'):
        if system_select == 'p': #POWER CYCLE ALL SUBSYSTEMS
            print("All systems will be toggled now...")
            if send_command(POWER_CYCLING, system_select) == -1:
                print("ERROR: error\n")

            time.sleep(BT_TXRX_WAIT)

            if check_ACK():
                print("All subsystems power cycled, success\n")
                try:
                    success = int(BT_SERIAL.read())
                    opower_state = int(1 - opower_state)
                    ipower_state = int(1 - ipower_state)

                except ValueError:
                    success = 0
                print("power cycle success: " + str(success))
            else:
                print("ERROR: Incorrect message received from bluetooth")
            
        elif system_select == 'o': #TOGGLE ORIENTATION CONTROL POWER
            print("Toggling orientation control system power...\n")

            if send_command(POWER_CYCLING, system_select) == -1:
                print("error\n")
            time.sleep(BT_TXRX_WAIT)
        
            if check_ACK() == 1:
                print("Orientation control power cycled, success\n")
                state_received = None

                while (state_received == None):
                    try:
                        state_received = int(BT_SERIAL.read())
                    except ValueError:
                        state_received = 0
                opower_state = state_received
            else:
                print("ERROR: Orientation system power did not send SUCCESS_ACK")
            
        elif system_select == 'i': #TOGGLE IMAGING SUBSYSTEM POWER
            print("Toggling imaging system power...\n")

            if send_command(POWER_CYCLING, system_select) == -1:
                print("ERROR: error\n")
            time.sleep(BT_TXRX_WAIT)
            
            if check_ACK() == 1:
            
                print("Imaging control power cycled, success\n")
                state_received = None

                while (state_received == None):
                    try:
                        state_received = int(BT_SERIAL.read())
                    except ValueError:
                        state_received = 0
                ipower_state = state_received
            else:
                print("ERROR: Imaging system power did not send SUCCESS_ACK")
           
        elif system_select == 't': #TOGGLE TELEMETRY SUBSYSTEM POWER
            print("Toggling telemetry system power...\n")

            if send_command(POWER_CYCLING, system_select) == -1:
                print("ERROR: error\n")
            time.sleep(BT_TXRX_WAIT)

            #get ack before telemetry shuts off
  
            if check_ACK() == 1:
                print("ACK recvd. Telemetry disconnecting, reconnecting after 10..\n")
                BT_SERIAL.close() # close the bluetooth connection

                for x in xrange(0, 6): # sleep 5 seconds
                    print (str(x) + '...')
                    time.sleep(1)

                global BT_SERIAL
                ## try to re-establish BT connection after time.sleep()
                BT_SERIAL = serial.Serial( 
                    port=bluetooth_COM,\
                    baudrate=COMS_BAUD,\
                    parity=serial.PARITY_NONE,\
                    stopbits=serial.STOPBITS_ONE,\
                    bytesize=serial.EIGHTBITS,\
                        timeout=0)   

                if TESTING:
                    time.sleep(2)
                    telescope.readline()
                    telescope.readline()
            else:
                print("ERROR: Telemetry system power toggle did not send \
                SUCCESS_ACK, keeping connection open")

        elif system_select == 'm': #RESET MICROCONTROLLER 
            print("RESETTING MSP430...\n")

            if send_command(POWER_CYCLING, system_select) == -1:
                print("ERROR: error\n")

            ##uC RESTARTS, USE BOOTUP READ LINE FUNCTION
            bootup() #clear buffer of startup data stream

        print("Orientation system powered? = " + str(opower_state))
        print("Telemetry system powered? = " + str(1))
        print("Imaging system powered? = " + str(ipower_state) + "\n\n")

        print("Select a system to power cycle (press 'e' to exit): \n\
                'p': Power on all subsystems \n\
                'o': Orientation control \n\
                'i': Imaging system \n\
                't': Telemetry system \n\
                'm': reset microcontroller")
        system_select = raw_input()
    global state
    state = 0
    return


def delta_steer():
    """ALlows user to adjust orientation of the telescope by a relative amount"""
    print("Steering mode (press 'e' to return to main menu):\n")
    print(current_coords)
    key = 0
    angleStep = 1
    angleDec = 0
    rightAsc = 0
    done = 0
    
    #press a key to count up or down, j\k to adjust increment size...
    while not (key == 'e') and not done:
        key = raw_input()
       
        if key == 'w':
            angleDec = angleDec + angleStep
        elif key == 's':
            angleDec = angleDec - angleStep
        elif key == 'd':
            rightAsc = rightAsc + angleStep
        elif key == 'a':
            rightAsc = rightAsc - angleStep
        elif key == 'j': #else change angleStep size
            angleStep = angleStep * 2
            print('anglestep: ' + str(angleStep))
        elif key == 'k':
            angleStep = angleStep / 2
            if angleStep == 0:
                angleStep = 0.5
            print('anglestep: ' + str(angleStep))

        print("rightAsc: " + str(rightAsc) + ", angleDec: " + str(angleDec) \
              + "\r")

        if key == "": 
            print("\nMove rightAsc: " + str(rightAsc) + ", angleDec: " + \
                  str(angleDec) + ' (deltas)? (y/n to confirm)')

            decision = 0

            while not(decision == 'y') and not (decision == 'n'):
                decision = raw_input()

            if decision == 'y':
                coords = [rightAsc, angleDec]
                if send_command(DELTA_STEER, coords) == -1: 
                    print("error\n")
                
                time.sleep(SERIAL_TXRX_WAIT)
                
                if check_ACK() == 1:
                    print("DELTA_STEER steer successful\n")

                    returned_ra = get_coord_from_scope()
                    current_coords[0] = uint16_to_deg(returned_ra)

                    returned_dec = get_coord_from_scope()
                    current_coords[1] = uint16_to_deg(returned_dec)
                    print("current_coords (ra, dec): ")
                    print(current_coords)
                
                else:
                    print("ERROR: DELTA_STEER steer did not rcv SUCCESS_ACK")
                    print("Returning to Menu")
                    global state
                    state = 0
                return
                    
            elif decision == 'n':
                #retry entry
                print("Send a new move command: ")


def navigate_to():
    """Allows user to enter a polar coordinate right ascension, declination, to send"""
    print("Navigate to point.....\n(press 'e' to exit):\n")
    angleDec = 0
    rightAsc = 0
    key = '0'
    
    done = 0

    while not (key == 'e'):
        ra = 0
        dec = 0
        
        print("Enter angle of right ascension: ")
        ra = raw_input()
        print("Enter angle of declination")
        dec = raw_input()

        if ra == 'e' or dec == 'e':
            key = 'e'
        else:
            try:
                ra = float(ra)
            except ValueError:
                print("could not convert angle to float")
                ra = 181
                
            while abs(ra) > 180:
                print("Enter angle of right ascension: ")
                ra = raw_input()
                try:
                    ra = float(ra)
                except ValueError:
                    print("could not convert ra to float")

            try:
                dec = float(dec)
            except ValueError:
                print("could not convert dec to float")
                dec = 91
                
            while abs(dec) > 90:
                print("Enter angle of declination: ")
                dec = raw_input()
                try:
                    dec = float(dec)
                except ValueError:
                    print("could not convert dec to float")
            
            destination = [ra, dec]

            print("\nMove to rightAsc: " + str(ra) + ", angleDec: " + str(dec) \
                  + ' (deltas)? (y/n to confirm)')

            decision = 0

            while not(decision == 'y') and not(decision == 'n'):
                decision = raw_input()

            if decision == 'y':
                if send_command(NAVIGATE_TO, destination) == -1: 
                    print("ERROR: error\n")
                
                if check_ACK() == 1:
                    print("Navigate to, successful\n")

                    returned_ra = get_coord_from_scope()
                    current_coords[0] = uint16_to_deg(returned_ra)

                    returned_dec = get_coord_from_scope()
                    current_coords[1] = uint16_to_deg(returned_dec)
                    print("MOVED TO " + str(current_coords))
                
                key = 'e' #signal done
                    
            elif decision == 'n':
                #retry entry
                print("Send a new move command: ")
                
'''
SENDS A USER DEFINED CHAR TO DSN BLOCK AND WAITS FOR REPLY
PRINTS THE RECVD CHAR ONCE RECEIVED
'''
def test_DSN():
    """Sends a user-defined char to DSN block and waits until received back
    
    Prints the elapsed time once character is received back.
    """
    
    recvd = None
  
    print("sending to DSN...")
    global DSN_TEST_CHAR
    time1 = time.time()
    DSN_SERIAL.writelines(DSN_TEST_CHAR)
    print('sent ' + DSN_TEST_CHAR)
    print('waiting...')
    time.sleep(SERIAL_TXRX_WAIT*2)

    while recvd == None:
        recvd = DSN_SERIAL.readline()
        time2 = time.time()
        
    print("Received from DSN: " + recvd + ' after ' + str(time2-time1) + ' seconds\n')
    return recvd


def get_coord_from_scope():
    """Reads an encoded uint16 coordinate from the Bluetooth serial COM port
    
    Args: 
        none
    
    Returns:
        angleCoordinate: integer value encoded angle from telescope
        """
    bit = BT_SERIAL.read()
    rx_data = bit
    while not (bit == "") and not (bit == '\n'):
        bit = BT_SERIAL.read()
        rx_data = rx_data + str(bit)

    time.sleep(SERIAL_TXRX_WAIT)
    
    if TESTING:
        print("Received from scope: " + str(rx_data))

    angleCoordinate = 0
    
    try:
        angleCoordinate = int(rx_data)
    except ValueError:
        print("ERROR: couldn't get integer angle coordinate")
        angleCoordinate = 0 ## reset to 0

    return angleCoordinate

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
            timeout=0) #simulated telescope receiving/sending port

#this port is used for communication with the DSN block before sending a command by BT
DSN_SERIAL = serial.Serial(
    port=DSN_COM,\
    baudrate=COMS_BAUD,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=0) #computer to CP2102 serial port, used for interfacing with the DSN

#used to pair with the telescope and send commands via the laptop's built in BT
BT_SERIAL = serial.Serial( 
    port=bluetooth_COM,\
    baudrate=COMS_BAUD,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=0) 

if DSN_SERIAL.isOpen() and BT_SERIAL.isOpen():          
    print("Computer connected to DSN on port: " + DSN_SERIAL.portstr + ", baudrate: " \
          + str(DSN_SERIAL.baudrate))
    print("Telescope " + bt_device + " connected to bluetooth via: " \
           + BT_SERIAL.portstr + ", baudrate: " + str(BT_SERIAL.baudrate))
    if TESTING:
        print("telescope simulator connected to " + str(telescope.portstr) \
              + ", testing...\n")
        
else:
    print("ERROR: Failed to open a serial port")


'''*********************************************'''        
'''              MAIN EXECUTIVE                 '''
'''*********************************************'''
while True:       
  
    if state == MENU:
        bootup() ##clears rx_buffer if msp 430 sends extra data
        
        #display menu selection and instructions
        print("Menu select: \n\
                1. Calibration \n\
                2. Subsystem power management \n\
                3. Relative angle adjustment -  free steering \n\
                4. Navigate to point \n\
                5. Save (disabled) \n\
                6. test_DSN()\n\
                7. Shutdown ")
        try:
            state = int(raw_input())
        except ValueError:
            state = MENU
            
    elif state == CALIBRATION:
        calibrate()

        data = BT_SERIAL.readline()
        print("residual data received from telescope: " + data)
        state = MENU

    elif state == POWER_CYCLING:
        print("Now in power cycling mode: ")

        power_cycle()

        state = MENU

    elif state == DELTA_STEER:
        print("Use 'w', 's', 'a', and 'd' keys to steer a relative number of degrees. \n\
                Use j/k to adjust the step value you wish to change by.")
        delta_steer()

        print("Now exiting angle-adjustment steering mode")

        state = MENU

    elif state == NAVIGATE_TO:
        print("Navigate to...")
        navigate_to()
        state = MENU

    elif state == SAVE:
        print("disabled")
        state = MENU
        
    elif state == SHUTDOWN:
        break
    
    elif state == DSN_TEST_STATE:
        test_DSN()
        state = MENU
print("closing serial ports..")
DSN_SERIAL.close()
BT_SERIAL.close()
