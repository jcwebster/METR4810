'''
THIS SCRIPT IS FOR TESTING SENDING COMMANDS TO THE MOTOR VIA HC06
'''
##testing send_command by sending a list

from __future__ import print_function
import os
import serial
import time

#testing variables:
TESTING = 0

#communication variables
COMS_BAUD = 1200
usbTTL_COM = 'COM3'
bluetooth_COM = 'COM10'

CALIBRATION = 1

def calibrate():
    print("Calibration mode\n")
    #calibrate here...
    print("Enter a char to send: \n")
    char_to_send = raw_input()

    if (send_command(CALIBRATION, char_to_send)):
        global finished
        finished = 1
    else:
        print("Error in sending command")
        return
    
def send_command(mode, command):

    a = 0
    while a < mode:
        a = a + 1
        bt_ser.writelines(command) # send directly 
 
    return 1

#may need to initialize settings in AT mode here (see todo 2.1 and then send AT+RESET
#to enter pairing mode... or would this algorithm be used on board...
bt_ser = serial.Serial( #used for testing right now
    port=bluetooth_COM,\
    baudrate=COMS_BAUD,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=0)              #Bluetooth to computer serial port connection, used to transmit and receieve commands from the telescope


while True:
    print("Enter a char to send, 'p' to exit: \n\
            1: send one copy of letters entered \n\
            2: send 50 copies of letters entered\n")
    char_to_send = raw_input()

    if char_to_send == 'p':
        break
    
    elif (char_to_send == '1'):
        while not (char_to_send == 'p'):
            print("Enter a char to send: \n")

            char_to_send = raw_input()

            send_command(1, char_to_send)
       
    elif (char_to_send == '2'):
        while not (char_to_send == 'p'):
            print("Enter a char to send: \n")

            char_to_send = raw_input()

            send_command(1, char_to_send)
    else:
        print("Error in sending command")

    if TESTING:
        rcvd = bt_ser.readline()
        time.sleep(WAITING_TIME)
        print(str(rcvd) + " received.")
        

print("closing serial ports..")
bt_ser.close()
