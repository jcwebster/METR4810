#send list to function test
##testing send_command by sending a list

from __future__ import print_function
import os
import serial
import time

#testing variables:
TESTING = 1
scope_COM = 'COM3'

#communication variables
COMS_BAUD = 1200
usbTTL_COM = 'COM12'
bluetooth_COM = 'COM5'
bt_device = "HC06"
SUCCESS_ACK = 1 # NEED TO ASK ANDY WHAT CHAR HE WOULD LIKE TO SEND AS AN ACK for success or failure
WAITING_TIME = 1  # CAUTION: adjust waiting time as necessary during testing, or add a while loop
DSN_DELAY = 1
WAITING_TIMEOUT = 9999


CALIBRATION = 1
##CALIBRATION VARIABLES
CALIBRATE_ROLL = 'F'
CALIBRATE_PITCH = 'G'
CALIBRATE_YAW = 'H'


def test():
    print("this is a test")

def check_ACK():
    ack = None
    a=0
    bt_ser.read() #CAUTION; EXTRA
    while (ack == None and a < WAITING_TIMEOUT):
        ack = bt_ser.read()
        a = a + 1

    if (a > WAITING_TIMEOUT):
        print ("timeout error; a = " + str(a))

    if (not (ack == '')):    
        if (int(ack) == SUCCESS_ACK):
            if TESTING:
                print("ACK success\n")
        else:
            print("WHAT?: " + ack)
    else:
        print('NACK received')

def calibrate():
    print("Beginning calibration...\n")
    #calibrate here...

    ## Send calibration command to begin yaw movement and set micro to rcv data for calibrating roll
    send_command(CALIBRATION, CALIBRATE_ROLL)

    '''
        response of telescope will either autonomously move yaw right and
        measure angle to roll, OR user will have to trace the path of motion
        and calculate the angle of correction manually and enter it here
    '''
    done = 0
    while (not done):       
        print('Telescope moved yaw [right]; enter roll correction angle (clockwise):')
        rollCorrection = raw_input()

        print('Correct roll by %f degrees? (y or n)' % float(rollCorrection))

        decision = raw_input()

        while (not(decision == 'y') or (decision == 'n')):
            print("invalid input")
            decision = raw_input()

        if (decision == 'y'):
            send_command(CALIBRATION, rollCorrection)
            done = 1
        else: #'n'
            print('please reenter roll correction...')

    if (not check_ACK()):
        print ('error checking ack')
        return
               
    # Spacecraft should pitch up to gimbal lock, then move down automatically
    # to 0deg pitch
    send_command(CALIBRATION, CALIBRATE_PITCH)
    check_ACK()
    
    #spins 360deg to calibrate MAG3110 and then uses N heading to point
    #at 0deg relative to Hawken Gallery
    send_command(CALIBRATION, CALIBRATE_YAW)

    check_ACK()
    
  
def send_command(mode, command, angle = 0):
    ret_val = 0
    done = 0
    if ((cp2102_ser.isOpen()) and (bt_ser.isOpen())):
        
        if (mode == CALIBRATION):        
            #send the same command that fnc was passed
            cp2102_ser.writelines(str(command))
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
                
        else:
            print("not testing calibration mode")
            ret_val = -1

        global TESTING
        if TESTING:
            if mode == CALIBRATION:
                telescope_sim_response(SUCCESS_ACK)
            else:
                telescope_sim_response(mode)
            print( "**SIMULATING SCOPE RESPONSE**")
    
        return ret_val
    else:
        print("error opening a serial port")
        return -1

    
    
def telescope_sim_response(mode):
    if ((telescope.isOpen()) and (bt_ser.isOpen())):
        rx_data = telescope.readline()
        time.sleep(WAITING_TIME) 
        print("telescope received: " + str(rx_data))
        #send response from telescope
        
        if mode == SUCCESS_ACK:
            telescope.writelines(str(mode)) 
            time.sleep(WAITING_TIME)
        elif mode == CALIBRATION:
            telescope.writelines(str(rx_data))
            time.sleep(WAITING_TIME)
            print("sent " + str(rx_data))
        else:
            telescope.writelines(str(rx_data))
            time.sleep(WAITING_TIME)
            print("sent " + str(rx_data))

if __name__ == '__main__': #calibration_Test.py executed as script
    
    if TESTING:
        telescope = serial.Serial(
            port=scope_COM,\
            baudrate=COMS_BAUD,\
            parity=serial.PARITY_NONE,\
            stopbits=serial.STOPBITS_ONE,\
            bytesize=serial.EIGHTBITS,\
                timeout=0)              #simulated telescope receiving/sending port (receieves bt_ser.write)

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
        if (TESTING):
            print("telescope simulator connected to port: " + telescope.portstr + ", baudrate: " + str(telescope.baudrate))
    else:
        print("Failed to open a serial port")


    while True:
        print("Testing calibration, press 'e' to exit... \n")
        char_to_send = raw_input()

        if char_to_send == 'e':
            break
        else:
            calibrate()
    ##    if (send_command(CALIBRATION, char_to_send)):
    ##        global finished
    ##        finished = 1
    ##    else:
    ##        print("Error in sending command")

        if TESTING:
            rcvd = bt_ser.readline()
            time.sleep(WAITING_TIME)
            print("received:" + str(rcvd))

    ##telescope_sim_response(CALIBRATION)

    ##time.sleep(1)

    print("closing serial ports..")
    cp2102_ser.close()
    bt_ser.close()
    telescope.close()
