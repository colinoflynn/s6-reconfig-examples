import serial
from RegisterInterface import RegisterInterface

def parseRbt(bgtname="diffbits.rbt"):
    f = open(bgtname, "r")

    bitsnow = False

    data = []

    for line in f:
        if bitsnow:
            data.append(int(line, 2))
        elif "Part" in line:
            part = line.split()[1]
        elif "1111111111111111" in line:
            data.append(int(line, 2))
            bitsnow = True

    return (part, data)

def main():
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


    #Load .rbt file
    #data = parseRbt("diffbits_24ma_fast.rbt")
    data = parseRbt("diffbits_2ma_fast.rbt")
    #data = parseRbt("diffbits_clkdiv2.rbt")


    if len(data[1]) > 2048:
        print "Default FIFO Only has room for 2048 commands! .rbt contains %d"%len(data[1])
        print "Will have to split .rbt file up in future...."
        sys.exit()

    dataToSend = [0x00]
    for d in data[1]:
        dataToSend.append(d >> 8)
        dataToSend.append(d & 0xff)

    reg.sendMessage(reg.CODE_WRITE, 52, dataToSend, Validate=False)
    reg.sendMessage(reg.CODE_WRITE, 52, [0x1A], Validate=False)
    reg.sendMessage(reg.CODE_WRITE, 52, [0x00])
    


main()
