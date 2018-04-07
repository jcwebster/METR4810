#send list to function test
##testing send_command by sending a list

pitch = 30
yaw  = 10
roll = -20

def send_command(mode, command):
    #if ((cp2102_ser.isOpen()) and (bt_ser.isOpen())):

    if (mode == 0 or mode == 1): 
        data_to_send = command        #send data that was received
        print(data_to_send + " received from DSN, sending...")
        return 1
    
    elif (mode == 2):
        
        return 1
    elif (mode == 3):
        print(str(command[0]) + " " + str( command[1]) + " " + str(command[2]))
##            print(pitch + roll + yaw)
##            print (coords['p'] + " " + coords['y'] + coords['r'])
        print("printed mylist..")
        return 1
    else:
        return -1
##else:
##    print("error opening a serial port")
##    return -1


coords = [pitch, yaw, roll]
if (send_command(3, coords) == -1): #CAUTION: NEED TO MAKE A LIST AND SEND
    print("error\n")

if (send_command(0, 't')):
    print( "success")
