# RUSH2svr.py
import struct
import ctypes
import os
from math import ceil
import socket

HOST = "127.0.0.1"
PORT = 54321


class RUSH2:
    """To transmit data based on the initial get request sent by client"""

    def __init__(self, header, fname=r'files/file.txt'):
        """header: header of the client
        fname: filename"""
        self.HEADER = '4H'
        self.DATASIZE = 1464

        # store previous header
        self.header = header
        # first time initialization
        self.buff = ctypes.create_string_buffer(self.DATASIZE + struct.calcsize(self.HEADER))
        self.b_offset = 0
        self.end = False
        self.chk = False
        self.enc = False
        self.retrans = 0
        # check data tranmission mode
        flags = []
        flag = header[3]
        for i in range(7, -1, -1):
            if flag // 2 ** i == 1:
                flags.append(True)
                flag -= 2 ** i
            else:
                flags.append(False)
        if flags[2] is True:
            self.chk = flags[5]
            self.enc = flags[6]
        if self.enc is True:
            fname = self.__decode(fname)
        # get data from file
        fname = r"{}".format(fname)
        with open(fname, "r") as f:
            self.data = f.read()
        # total size of data
        self.dsize = len(self.data)
        # offset for packet transmission
        self.poffset = 0
        self.psize = ceil(self.dsize / self.DATASIZE)
        # storing each packet transmitted
        self.pdata = [b'\x00']

        # initialize outgoing header param
        self.seq = 1
        self.ack = 0
        self.flags = 0
        self.checksum = 0
        self.version = 1

    def set_header(self, header):
        # reset flags
        self.ack = 0
        self.flags = 0
        seq, ack, cksum, flag, ver = header
        seq = struct.unpack('!H', seq)[0]
        ack = struct.unpack('!H', ack)[0]
        cksum = struct.unpack('!H', cksum)[0]
        flags = []
        for i in range(7, -1, -1):
            if flag // 2 ** i == 1:
                flags.append(True)
                flag -= 2 ** i
            else:
                flags.append(False)
        print('flags=', flags)
        # print('prevheader', self.header)
        # chk and enc flag
        if self.chk is True:
            self.flags += 0x0400
        if self.enc is True:
            self.flags += 0x0200
        # check data or get flag
        if flags[3] is True or flags[2] is True:
            if not self.end:
                self.flags += 0x1000
            else:
                self.flags += 0x0800
            # check for ack from client
            if flags[0] is True and flags[1] is not True:
                # set ack to self.flags
                self.ack = seq
                self.flags += 0x8000
            # check for nack
            if flags[1] is True and flags[0] is not True:
                # retransmit seq num
                self.retrans = ack
                self.ack = seq
                self.flags += 0x8000
                # offset increment
                self.seq -= 1
            # update previous header
            self.header = header
            return True

        return False

    def pack(self, header):
        """Create packets for transmission"""
        # set header
        if self.set_header(header) is True:
            # reset buffer and offset
            self.b_offset = 0
            self.buff = ctypes.create_string_buffer(self.DATASIZE + struct.calcsize(self.HEADER))
        else:
            return False
        # prepare data
        if not self.end and self.retrans == 0:
            if self.poffset < self.dsize:
                # standard size
                if self.enc is True:
                    data = self.__encode(self.data[self.poffset:self.poffset + 1463].encode("utf-8"))
                else:
                    data = self.data[self.poffset:self.poffset + 1463].encode("utf-8")
                self.pdata.append(data)
                self.poffset += 1463
            else:
                # last packet
                if self.enc is True:
                    data = self.__encode(self.data[self.poffset:].encode("utf-8"))
                else:
                    data = self.data[self.poffset:].encode("utf-8")
                self.pdata.append(data)
                self.end = True
        # pushing header into buffer
        self.__push(form='!H', value=self.seq)
        self.__push(form='!H', value=self.ack)
        if self.chk is True:
            # implement check sum
            self.checksum = self.__get_sum(self.pdata[-1] if self.retrans == 0 else self.pdata[self.retrans])
        self.__push(form='!H', value=self.checksum)
        # self.flags = 0x800
        self.__push(form='!H', value=self.flags + self.version)
        # push data into the buffer
        if self.retrans != 0:
            # retransmitting the nack/ unack packet
            self.__push(form='1464s', value=self.pdata[self.retrans])
            self.retrans = 0
        else:
            self.__push(form='{}s'.format(len(self.pdata[-1])), value=self.pdata[-1])
        # seq increment
        self.seq += 1
        return True

    def send_packet(self):
        print('out_data: ', self.buff.raw[:20])
        print()
        return self.buff.raw

    def __push(self, form, value):
        struct.pack_into(form, self.buff, self.b_offset, value)
        self.b_offset += struct.calcsize(form)

    def __get_sum(self, data):
        count = 0
        data = data.decode("utf-8")
        for i in range(0, len(data), 2):
            if len(data) - i == 1:
                count += int(hex(ord(data[-1]))[2:], 16)
                break
            value = '0x{}{}'.format(hex(ord(data[i + 1]))[2:], hex(ord(data[i]))[2:])
            count += int(value, 16)
        return int(hex(0xFFFF - count % 0xFFFF), 16)

    def __decode(self, data):
        out = ''
        for char in data:
            char = ord(char) - 3
            out = out + chr(char if char >= 0 else char + 127)
        return out

    def __encode(self, data):
        out = ''
        # iterating using string
        data = data.decode("utf-8")
        for char in data:
            # encoding
            out = out + chr((ord(char) + 3) % 127)
        # return bytestring
        return out.encode()


class Rush:
    """Add the header file to the bytes data"""

    def __init__(self, data, header):
        """data: bytes format with max 1464 bytes"""
        # Header format: sequence number, ack numberm checksum, flags, reserved, version code
        MAX_DATA_SIZE = 1464
        self.header = header
        self.seqNum = 1
        self.ackNum = 0
        self.offset = 0
        self.flags = [False for i in range(7)]
        # [seq, ack, checksum, flag, version]
        '''
        if bytes == type(data):
            # check if the type is correct
            self.data = data
            # check how many dataframes are required
            self.data_size = len(data)
            # number of packets required to send all data
            self.packet_number = ceil(len(data) / MAX_DATA_SIZE)
        '''
        # create a buffer for the header
        self.buff = ctypes.create_string_buffer(1472)
        # self.create_packets()
        print(self.buff)

    def set_header(self, header):
        self.header = header

    def create_packets(self):
        # check flags
        if self.header[3] == 0x2000:
            # get request
            filename = 0
        self.__push('!H', self.seqNum)
        self.__push('!H', self.ackNum)
        self.__push('H', 0)
        # flags and version
        if self.header[3] == 0X88:
            self.__push('!H', 0X8801)
        else:
            self.__push('!H', 0X801)
        # reset the offset
        self.offset = 0
        self.seqNum += 1
        self.ackNum += 1

    def __push(self, format, value):
        struct.pack_into(format, self.buff, self.offset, value)
        self.offset += struct.calcsize('H')


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        while True:
            try:
                data, addr = s.recvfrom(1500)
                header = []
                # get seq, ack, checksum
                for i in range(0, 6, 2):
                    header.append(data[i:i + 2])
                # get flags and version
                header.append(data[6])
                header.append(data[7])
                print('in_header: ', header)
                # format data
                data = data[8:]
                data = data.decode("utf-8")
                data = data.strip('\x00')
                print('in_data: ', data)
                if header[3] == 0x20 or header[3] == 0x24 or header[3] == 0x22 or header[3] == 0x26:
                    test = RUSH2(header, data)
                    test.pack(header)
                    s.sendto(test.send_packet(), addr)
                    s.settimeout(4.0)
                    continue
                if test.pack(header) is True:
                    s.sendto(test.send_packet(), addr)
                if test.end is True:
                    test.pack([b'\x00\x00', b'\x00\x00', b'\x00\x00', 0x10, 1])
                    s.sendto(test.send_packet(), addr)
                    if header[3] == 0x88 or header[3] == 0x8C or header[3] == 0x8E:
                        print('End of communication')
                        break
                # set timeout
                s.settimeout(4.0)
            except socket.timeout:
                # resend due to timeout
                print('resend due to timeout')
                s.sendto(test.send_packet(), addr)


def main1():
    test = RUSH2(['b\x00\x00', 'b\x00\x00', 'b\x00\x00', 0, 1])
    print(test.data)


if __name__ == '__main__':
    main()
