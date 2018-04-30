#send list to function test
##testing send_command by sending a list

from __future__ import print_function
import os
import serial
import time

#testing variables:
TESTING = 1
scope_COM = 'COM14'

#communication variables
COMS_BAUD = 1200 # limited by DSN
DSN_COM = 'COM3'
bluetooth_COM = 'COM5'
bt_device = "HC06"
SUCCESS_ACK = 1 # NEED TO ASK ANDY WHAT CHAR HE WOULD LIKE TO SEND AS AN ACK for success or failure
WAITING_TIME = 1  # CAUTION: adjust waiting time as necessary during testing, or add a while loop
DSN_DELAY = 1
WAITING_TIMEOUT = 9999


CALIBRATION = 1
##CALIBRATION VARIABLES
CALIBRATE_ROLL = 'F' #commands telescope to steer YawRight and measure angle to correct the roll
#- or if it doesn't, it waits for an angle to roll sent by user at ground
CALIBRATE_PITCH = 'G' #scope moves up to lcoking point then steers back down to 0deg pitch 
CALIBRATE_YAW = 'H'  #scope rotates 360deg to calibrate MAG3110 magnetometer


def test():
    print("this is a test")

def check_ACK():
    ack = None
    a=0
##    bt_ser.read() #CAUTION; EXTRA
    while (ack == None and a < WAITING_TIMEOUT):
        ack = bt_ser.read()
        a = a + 1

    if (a > WAITING_TIMEOUT):
        print ("timeout error; a = " + str(a))

    if (not (ack == '')):    
        if (ack == str(SUCCESS_ACK)):
            if TESTING:
                print("ACK received by ground control.\n")
        else:
            print("WHAT?: " + ack)
        return 1
    else:
        print('NACK received')
        return 0

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
                rollCorrection = raw_input()

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
        rcvd = bt_ser.readline()
        time.sleep(WAITING_TIME)
        print("received:" + str(rcvd))

    global state
    state = 0
    return
  
def send_command(mode, command, angle = 0):
    ret_val = 0
    if ((DSN_SERIAL.isOpen()) and (bt_ser.isOpen())):
        
        if (mode == CALIBRATION):        
            #send the same command that fnc was passed
            DSN_SERIAL.writelines(str(command))
            time.sleep(WAITING_TIME)
            data_to_send = None
            
            print("sending to DSN...")
            time.sleep(DSN_DELAY) 
            data_to_send = DSN_SERIAL.readline()
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
        elif mode == CALIBRATION: ##WILL NEVER EXECUTE BC SUCCESS_ACK AND CALIBRATION ARE == 1
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

    DSN_SERIAL = serial.Serial(
        port=DSN_COM,\
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

    if ((DSN_SERIAL.isOpen()) and (bt_ser.isOpen())):
                    
        print("Computer CP2102 connected to: " + DSN_SERIAL.portstr + ", baudrate: " + str(DSN_SERIAL.baudrate))
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
    DSN_SERIAL.close()
    bt_ser.close()
    telescope.close()
