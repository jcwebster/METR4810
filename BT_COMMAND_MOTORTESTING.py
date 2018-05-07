'''
THIS SCRIPT IS FOR TESTING SENDING COMMANDS TO THE MOTOR VIA HC06

User enters 1 or 2 and then the character command for motors

The script requires pyserial to be installed.
Set up the bluetooth connection by finding the Bluetooth COM port under
Devices and Printers --> Device--> Device Properties
'''

from __future__ import print_function
import os
import serial
import time

#testing variables:
TESTING = 0

#communication variables
COMS_BAUD = 1200
bluetooth_COM = 'COM10'

CALIBRATION = 1

def send_command(mode, command):

    a = 0
    while a < mode:
        a = a + 1
        bt_ser.writelines(command) # send directly 
 
    return 1

## Serial connection initialisation
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
