import serial
import time
''' TODO:

- readstr is only reading a character from the rx buffer every second time, if at all..
NEED A DELAY BEWTWEEN SENDING AND READING MIRRORED INPUT ON USB-TTL
'''
COMS_BAUD = 1200
usbTTL_COM = 'COM9'
bluetooth_COM = 'COM5'
bt_device = "HC06"
'''
def send_command(mode, command):
    if ((cp2102_ser.isOpen()) and (bt_ser.isOpen())):

        if (mode == CALIBRATION or mode == POWER_CYCLING or mode == SAVE): 
            cp2102_ser.writelines(command)
            data_to_send = None
            
    #CAUTION: need to implement a wait or while loop for reading?
            print("waiting...")
            time.sleep(DSN_DELAY) #could remove
            
            #Need to test this more thoroughly
            while (data_to_send == None):
                #pass
                data_to_send = cp2102_ser.readline()

            #send data that was received
            print(data_to_send + " received from DSN, sending...")
            bt_ser.writelines(data_to_send)
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

count=1

while (count<5):

    print("enter string to send: ")
    sendstr = raw_input()
    cp2102_ser.writelines(sendstr)
    print("sent string: " + sendstr)

    time.sleep(1)
    readstr = cp2102_ser.readline()
    print("received on mirrored cp2102: " + str(readstr))
    
    time.sleep(3)
    line = bt_ser.readline()
    print("received string: " + line)
    
    count = count + 1
    
print("closing serial ports..")
cp2102_ser.close()
bt_ser.close()
    

