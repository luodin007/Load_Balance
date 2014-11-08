'''
Created on Jun 3, 2014

@author: luoding
'''

import socket
import CpuUsage
import time
import threading

class UDP_Server(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self) 
        self.HOST = '192.168.1.102'
        self.PORT = 8000
        self.BUFSIZE = 1024
        self.BEAT_PERIOD = 1
        self.ADDR = (self.HOST, self.PORT)
    
    def run(self):
        udpCliSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        cpuusage = CpuUsage.CpuUsage()

        while True:
            cpu1 = str(cpuusage.getCpuUsage())
            udpCliSock.sendto(cpu1, self.ADDR)
            print 'cpu usage: ',cpu1
            time.sleep(self.BEAT_PERIOD)
    
