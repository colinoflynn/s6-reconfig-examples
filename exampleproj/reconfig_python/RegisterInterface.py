# -*- coding: cp1252 -*-

#Copyright Colin O'Flynn 2014

import sys
import time
import datetime
from functools import partial

class RegisterInterface(object):
    CODE_READ       = 0x80
    CODE_WRITE      = 0xC0
    
    def __init__(self, serial_instance):
        super(RegisterInterface, self).__init__()
        self.serial = serial_instance        
        self.timeout = 5

        #Send clearing function
        nullmessage = bytearray([0]*20)        
        self.serial.write(str(nullmessage));
         
    
    def sendMessage(self, mode, address, payload=None, Validate=True, maxResp=None, readMask=None):
        """Send a message out the serial port"""

        if payload is None:
          payload = []

        #Get length
        length = len(payload)

        if ((mode == self.CODE_WRITE) and (length < 1)) or ((mode == self.CODE_READ) and (length != 0)):
            self.log("Invalid payload for mode")
            return None

        if mode == self.CODE_READ:
              self.flushInput()

        #Flip payload around
        pba = bytearray(payload)
        
        ### Setup Message
        message = bytearray([])

        #Message type
        message.append(mode | address)
       
        #Length
        lenpayload = len(pba)
        message.append(lenpayload & 0xff)
        message.append((lenpayload >> 8) & 0xff)

        #append payload
        message = message + pba

        ### Send out serial port
        self.serial.write(str(message))

        #for b in message: print "%02x "%b,
        #print ""               

        ### Wait Response (if requested)
        if (mode == self.CODE_READ):
            if (maxResp):
                datalen = maxResp           
            else:
                datalen = 1
            
            result = self.serial.read(datalen)

            #Check for timeout, if so abort
            if len(result) < 1:
                print "Timeout in read: %d"%len(result)
                return None

            rb = bytearray(result)

            return rb
        else:
            if Validate:
                check = self.sendMessage(self.CODE_READ, address, maxResp=len(pba))
                
                if readMask:
                    try:
                        for i,m in enumerate(readMask):
                            check[i] = check[i] & m
                            pba[i] = pba[i] & m
                    except IndexError:
                        pass
                
                if check != pba:
                    errmsg = "For address 0x%02x=%d"%(address,address)
                    errmsg +=  "  Sent data: "
                    for c in pba: errmsg += "%02x"%c
                    errmsg += "\n"
                    errmsg += "  Read data: "
                    if check:
                        for c in check: errmsg += "%02x"%c
                        errmsg += "\n"
                    else:
                        errmsg += "<Timeout>"
                        
                    print errmsg

    def flushInput(self):
        try:
           self.serial.flushInput()
        except AttributeError:
           return

if __name__ == "__main__":
    import serial
    
    ser = serial.Serial()
    ser.port     = "com6"
    ser.baudrate = 38400
    ser.timeout  = 1.0
    
    try:
        ser.open()
    except serial.SerialException, e:
        print "Could not open %s"%ser.name
        sys.exit()
    except ValueError, s:
        print "Invalid settings for serial port"
        ser.close()
        ser = None
        sys.exit()

    reg = RegisterInterface(ser)

    #Write RESET to partial reconfig register
    print "Enabling RESET"
    reg.sendMessage(reg.CODE_WRITE, 52, [0x20])
    print "0x%02x"%reg.sendMessage(reg.CODE_READ, 52)[0]

    print "Disabling RESET"
    reg.sendMessage(reg.CODE_WRITE, 52, [0x00])
    print "0x%02x"%reg.sendMessage(reg.CODE_READ, 52)[0]
    
