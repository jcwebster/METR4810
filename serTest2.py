import serial
import time
''' TODO:

 #create a test for send_commmand
'''

bt_device = "HC06"
'''
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
cp2102_ser = serial.Serial(
    port='COM9',\
    baudrate=9600,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=0)

bt_ser = serial.Serial(
    port='COM5',\
    baudrate=9600,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=0)


print("Computer CP2102 connected to: " + cp2102_ser.portstr + ", baudrate: " + str(cp2102_ser.baudrate))
print("Bluetooth " + bt_device + " connected to: " + bt_ser.portstr + ", baudrate: " + str(bt_ser.baudrate))
count=1

while (count<5):

    print("enter string to send: ")
    sendstr = raw_input()
    cp2102_ser.writelines(sendstr)
    print("sent string: " + sendstr)

    time.sleep(10)
    readstr = cp2102_ser.readline()
    print("received on mirrored cp2102: " + str(readstr))
    
    time.sleep(5)
    line = bt_ser.readline()
    print("received string: " + line)
    
    count = count + 1
    
print("closing serial ports..")
cp2102_ser.close()
bt_ser.close()
    

