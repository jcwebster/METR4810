##test_DSN Function

from __future__ import print_function
import os
import numpy as np
##import cv2
import time
import serial

#communication variables
COMS_BAUD = 1200 #set baudrate of communication between all devices # limited by DSN
DSN_COM = 'COM3'
bluetooth_COM = 'COM5'
bt_device = "HC06"
SUCCESS_ACK = 1 # NEED TO ESTABLISH AN ACK for success or failure
SERIAL_TXRX_WAIT = 0.5  # 500ms delay sending/reading serial
DSN_DELAY = 1
RX_TIMEOUT = 9999
scope_COM = 'COM14'

TESTING = 1
TEST_DSN = 7

#dsn_test variables
DSN_TEST_CHAR = '1'

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

if TESTING:
    device = telescope
else:
    device = DSN_SERIAL

if ((DSN_SERIAL.isOpen()) and (device.isOpen()) ):
                
    print("Computer CP2102 connected to: " + DSN_SERIAL.portstr + ", baudrate: " + str(DSN_SERIAL.baudrate))
    print("receiver connected to: " + device.portstr + ", baudrate: " + str(device.baudrate))
else:
    print("Failed to open a serial port")
'''
SENDS A USER DEFINED CHAR TO DSN BLOCK AND WAITS FOR REPLY
PRINTS THE RECVD CHAR ONCE RECEIVED
'''
def test_DSN():
    global TESTING
    recvd = None

    
    print("sending to DSN...")
    global DSN_TEST_CHAR
    DSN_SERIAL.writelines(DSN_TEST_CHAR)
    print('sent ' + DSN_TEST_CHAR)
    print('waiting...')
    time.sleep(SERIAL_TXRX_WAIT)

    while recvd == None:
        recvd = device.readline()
        
    print("Received from DSN: " + recvd + '\n')
    return recvd

a=0

while (a< 3):
    #call test_dsn function

    state = 0
    state = test_DSN()
##    print(state)

    time.sleep(1)

    a = a + 1
