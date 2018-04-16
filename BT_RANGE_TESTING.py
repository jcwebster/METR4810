#send list to function test
##testing send_command by sending a list

from __future__ import print_function
import os
import serial
import time
# CURRENTLY UNTESTED
# need to implement fake BT responses from the bt_testing com port
pitch = 30
yaw  = 10
roll = -20

#testing variables:
TESTING = 1
bluetoothRX_Testing = 'COM4'

#communication variables
COMS_BAUD = 1200
usbTTL_COM = 'COM3'
bluetooth_COM = 'COM5'
bt_device = "HC06"
SUCCESS_ACK = 1 # NEED TO ASK ANDY WHAT CHAR HE WOULD LIKE TO SEND AS AN ACK for success or failure
WAITING_TIME = 1  # CAUTION: adjust waiting time as necessary during testing, or add a while loop
DSN_DELAY = 1

CALIBRATION = 1

   
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
        print("Error in sending command")
        return
    
def send_command(mode, command):
    cp2102_ser.writelines(command)
    data_to_send = None
    
    print("waiting...")
    time.sleep(WAITING_TIME) 
    data_to_send = cp2102_ser.readline()

    #send data that was received
    print(data_to_send + " received from DSN, sending...")
    bt_ser.writelines(data_to_send)
    time.sleep(WAITING_TIME)

    global TESTING
    if TESTING:
        telescope_sim_response(mode)
    else:
        print('*not testing, waiting for response from telescope*')
    return 1

    
def telescope_sim_response(mode):
    if ((telescope.isOpen()) and (bt_ser.isOpen())):
        rx_data = telescope.readline()
        time.sleep(WAITING_TIME) 
        print("telescope received: " + str(rx_data))
        #send response from telescope
##        telescope.writelines(str(SUCCESS_ACK))
##        print("sent ack")

        telescope.writelines(str(rx_data))
        print("sent " + str(rx_data))


telescope = serial.Serial(
    port=bluetoothRX_Testing,\
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


coords = [pitch, yaw, roll]
data = 'p'

while True:
    print("Enter a char to send: \n")
    char_to_send = raw_input()

    if (send_command(CALIBRATION, char_to_send)):
        global finished
        finished = 1
    else:
        print("Error in sending command")

    if TESTING:
        rcvd = bt_ser.readline()
        time.sleep(WAITING_TIME)
        print(str(rcvd) + " received.")
    
        

##telescope_sim_response(CALIBRATION)

##time.sleep(1)

ack = bt_ser.read()
data2 = bt_ser.read()
print("data received from bluetooth: " + ack + " " + data2)

