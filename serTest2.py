import serial
import time

ser1 = serial.Serial(
    port='COM3',\
    baudrate=9600,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=0)

ser2 = serial.Serial(
    port='COM5',\
    baudrate=9600,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=0)

print("Computer CP2102 connected to: " + ser1.portstr)
print("Bluetooth HC06 connected to: " + ser2.portstr)
count=1

while True:

    sendstr = "Test data\n\r"
    ser1.writelines(sendstr)
    print("sent string: " + sendstr)

    time.sleep(10)
    line = ser2.readline()
    print("received string: " + line)
    
ser.close()
