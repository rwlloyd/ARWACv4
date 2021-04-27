import sys
import numpy as np
from numpy import inf
import cv2
import os 
from socket import * 
from decimal import Decimal
############################################################
class CRaspiScketUDPClient(object):
    '''
        # as client
        # Message Sender 
    '''
    def __init__(self, sock=None):
        # self.host ="10.101.12.90" "192.168.1.10" # set to IP address of target computer : TX2
        # self.host = "10.101.8.30" #"192.168.1.12" # set to IP address of target computer : TX1
        self.host ="10.101.12.90"
        self.port = 13000 
        self.addr = (self.host, self.port) 
        self.UDPSock = socket(AF_INET, SOCK_DGRAM) 

    def Data2Send(self, msg): 
        # self.data = msg.encode('utf-8')
        self.data = str(msg).encode('utf-8')
        self.UDPSock.sendto(self.data, self.addr) 

    def Clent2Close(self):
        self.UDPSock.close() 
        os._exit(0)

class CRaspiScketUDPSever(object):    
    '''
        # as server
        # Message Receiver 
    '''
    def __init__(self, sock=None):
        self.host = ""#"192.168.1.12"  # should be the addres of caller
        self.port = 13000 
        self.buf = 1024 
        self.addr = (self.host, self.port) 
        self.UDPSock = socket(AF_INET, SOCK_DGRAM) 
        self.UDPSock.bind(self.addr)         
        print ("Waiting to receive messages ...")


    def Sever2Close(self):
        self.UDPSock.close() 
        os._exit(0)


    """
    def jetsend(self, msg):
        totalsent = 0
        MSGLEN = len(msg)
        while totalsent < MSGLEN:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def jetreceive(self):
        chunks = []
        bytes_recd = 0
        while bytes_recd < MSGLEN:
            chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
            if chunk == '':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return ''.join(chunks)
    """
    def RasSend(self, msg):
        totalsent = 0
        MSGLEN = len(msg)
        while totalsent < MSGLEN:
            sent = self.UDPSock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def RasReceive_msg(self, EOFChar='\036'):

        (self.data, self.addr) = self.UDPSock.recvfrom(self.buf) 
        # print ("Received message: " + self.data.decode('utf-8'))
        print ("Received message from {sender} ".format(sender = self.addr))
        data= self.data.decode('utf-8')
        # print ("Received message: " + data)
        text = eval('[' + data + ']')
        return text

    def RasReceive_data(self, EOFChar='\036'):

        (self.data, self.addr) = self.UDPSock.recvfrom(self.buf) 
        # print ("Received message: " + self.data.decode('utf-8'))
        print ("Received message from {sender} ".format(sender = self.addr))
        data= self.data.decode('utf-8')
        # print ("Received message: " + data)
        # text = eval('[' + data + ']')
        return data
        """        
        msg = ''
        MSGLEN = 100        
        while len(msg) < MSGLEN:
            chunk = self.UDPSock.recv(MSGLEN-len(msg))
            if chunk.find(EOFChar) != -1:
                msg = msg + chunk
                return msg
            msg = msg + chunk
            return msg
        """


        """while True: 
            (self.data, self.addr) = self.UDPSock.recvfrom(self.buf) 
            # print ("Received message: " + self.data.decode('utf-8'))
            if self.data == "exit": 
                break """


def main():
    print('calling....')

if __name__ == '__main__':
    main()
