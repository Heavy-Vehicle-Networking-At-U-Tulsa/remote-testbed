import socket, struct, time, sys, binascii
from tornado import gen
import os
import subprocess, shlex

class CanTools():
    def __init__(self, interface):
        self.interface = interface
        self.canSocket = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)

        try:
            self.canSocket.bind((interface,))
        except OSError:
            sys.stderr.write("Could not bind to interface '%s'\n" % interface)
        self.canSocket.settimeout(5)
        self.format = '<IB3x8s'
    
    def readMessageRaw(self): #used in readMessage
        return self.canSocket.recv(16) #receive 16 bytes

    def readMessage(self): #used for logging and updating parameters. Candump format
    #used to gain more control over read messages. Read one at a time. Pair with Timestamp. Order.
        canPacket = self.readMessageRaw()
        canId, length, data = struct.unpack(self.format, canPacket)
        canId &= socket.CAN_EFF_MASK
        canId = ('%02x' % canId).upper()
        while len(canId) < 8:
            canId = '0' + canId
        data = data[:length].hex().upper()
        n = 2
        data = [data[i:i+n] for i in range(0,len(data),n)]
        message = (self.interface + " " + canId + " [" + str(length) +"] " + " ".join(data))
        return message
    
    def readBytes(self, canPacket): #not used
        canId, length, data = struct.unpack(self.format, canPacket)
        canId &= socket.CAN_EFF_MASK
        canId = ('%02x' % canId).upper()
        while len(canId) < 8:
            canId = '0' + canId
        data = data[:length].hex().upper()
        n = 2
        data = [data[i:i+n] for i in range(0, len(data),n)]
        print("  " + self.interface, end="  ")
        print(canId + "  [" + str(length) +"]", end = "  ")
        print(" ".join(data))

    @gen.coroutine
    def sendMessage(self, canId, length, payload): #used when sending scheduled CAN message
        #using cansend/cangen creates socket object each time it is used. This uses preexisting socket for quicker message sending.
        if len(str(canId)) > 3:
            self.canId = canId | 1 << 31 #This sets IDE Flag
        else:
            self.canId = canId
        self.canPacket = struct.pack(self.format, self.canId, length, payload)
        #self.canSocket.send(b"\x00\x01\xf0\x88\x08\x00\x00\x00\x11\x22\x33\x44\x55\x66\x77\x88")
        self.canSocket.send(self.canPacket)

    def sendMessage_noco(self, canId, length, payload): #used for parameter updates (not coroutine)
        #using cansend/cangen creates socket object each time it is used. This uses preexisting socket for quicker message sending.
        if len(str(canId)) > 3:
            self.canId = canId | 1 << 31 #This sets IDE Flag
        else:
            self.canId = canId
        self.canPacket = struct.pack(self.format, self.canId, length, payload)
        #self.canSocket.send(b"\x00\x01\xf0\x88\x08\x00\x00\x00\x11\x22\x33\x44\x55\x66\x77\x88")
        self.canSocket.send(self.canPacket)

    @gen.coroutine
    def vinUpdate(self, new_vin): #updates VIN
        #uses cansend here and works. Governor speed had to use sendMessage_noco to work properly. 
        subprocess.run(["cansend", "can1", "18DA00F1#0227050000000000"])
        found = False
        keydone = False
        while not found and not keydone:
            msg = self.readMessage().split(" ")
            if msg[1] == "18DAF100":
                if msg[3:6] == ['04', '67' ,'05']:
                    print("Content Check Passed")
                    seed = ''.join(msg[6:8])
                    print("Seed: " + seed)
                    if seed == "0000":
                        print("Seed-key exchange done already")
                        keydone = True
                    else:
                        key = (0x8c*(int(seed,16)-1)+ 0x2710) % 0x10000
                        subprocess.run(["cansend", "can1", "18DA00F1#042706{:04X}000000".format(key)]) 
                        found = True
        print("Broken")
        id = "18DA00F1"
        defaultPart = "10142EF1A0"
        while len(new_vin) < 17:
            new_vin += " "
        vinBytes = binascii.hexlify(new_vin.encode())
        vinfirst = defaultPart + vinBytes[0:6].decode()
        vinsecond = "21" + vinBytes[6:20].decode()
        vinthird = "22" + vinBytes[20:].decode()
        subprocess.run(["cansend", "can1", id + "#" + vinfirst])
        subprocess.run(["cansend", "can1", id + "#" + vinsecond])
        subprocess.run(["cansend", "can1", id + "#" + vinthird])

    @gen.coroutine
    def govSpeedUpdate(self, gov_speed):
        print("Updating Gov. Speed")
        found = False
        keydone = False
        canid = 0x18DA00F1
        self.sendMessage_noco(canid, 8, b"\x02\x27\x05\x00\x00\x00\x00\x00")
        while not found and not keydone:
            msg = self.readMessage().split(" ")
            if msg[1] == "18DAF100":
                if msg[3:6] == ['04', '67' ,'05']:
                    print("Content Check Passed")
                    seed = ''.join(msg[6:8])
                    print("Seed: " + seed)
                    if seed == "0000":
                        keydone = True
                        print("Seed-Key exchange done already")
                    else:
                        key = (0x8c*(int(seed,16)-1)+ 0x2710) % 0x10000
                        payloadstr = struct.pack(">3sH3s", b"\x04\x27\x06", key, b"\x00\x00\x00")
                        self.sendMessage_noco(canid, 8, payloadstr) 
                        found = True
        found1 = False
        print("Entering second while")
        while not found1 and not keydone:
            msg = self.readMessage().split(" ")
            if msg[1] == "18DAF100":
                if msg[3:6] == ['02', '67', '06']:
                    print("Key passed")
                    self.sendMessage_noco(canid, 8, b"\x10\x0D\x2E\xF1\x5C\x00\x00\x00")
                    found1 = True
        found2 = False
#        while not found2:
#            msg = self.readMessage().split(" ")
#            if msg[1] == "18DAF100":
#                if msg[3:6] == ['30', '08', '14']:
        if not keydone:
            self.sendMessage_noco(canid, 8, b"\x21\x12\x03\x09\xC5\x0B\x82\x84")
#                    found2 = True
        print("Sleeping")
        time.sleep(.2)
        gov_speed_conv = int(gov_speed/.0049)
        if gov_speed_conv > 0xFFFF:
            gov_speed_conv = 0xFFFF
        gov_speed_str = struct.pack(">sH5s",b"\x26",gov_speed_conv, b"\x61\xFB\x1F\x40\x05")
        messages = [b'\x10\x52\x2E\x02\x03\x03\x1C\x20', b'\x21\x00\x83\x40\x1F\x40\x06\x40',
        b'\x22\x00\x0F\x00\xA0\x00\x01\x2C',
        b'\x23\x16\x00\x00\x0F\x38\x40\x00', b'\x24\x40\x2C\x56\x24\x34\x04\x00',
        b'\x25\x15\xE0\x7D\x00\x0F\x61\xA8', gov_speed_str,
        b'\x27\x00\x12\xC0\x11\x30\x03\x20', b'\x28\x01\x00\x00\x80\x00\x00\x00',
        b'\x29\x01\x00\x04\x00\x00\x01\x00', b'\x2A\x34\x80\xFF\xFF\xFF\xFF\xFF',
        b'\x2B\xFF\x01\x12\xC0\x00\x00']
        for message in messages:
            self.sendMessage_noco(canid, 8, message)


    @gen.coroutine
    def sendRawMessage(self, *rawMessage): #not used
        print("checkpoint")
        import array
        bytestring = bytes((list(rawMessage)))
        print(bytestring)
        print('sending {}'.format(bytestring))
        self.canSocket.send(bytestring)
        print('sent successfully')
    
if __name__ == '__main__':
    can = CanTools('can1')
    while(True):
        can.canSocket.send(b'\xf1\x00\xda\x98\x08\x00\x00\x00\x02\x27\x05\x00\x00\x00\x00\x00')

