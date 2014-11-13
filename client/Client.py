'''
Created on Jun 10, 2014

@author: luoding
'''
import socket
import random
import threading
import time
import traceback

taskNum = (1,3)
host = 'localhost'  
port = 8080 
bufsize = 1024  
addr = (host,port) 
rate = 0.1

def choice_task():
    return random.randint(1,3)

class Client(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self) 

    def run(self):
        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)  
        client.connect(addr)  
        while True:
            try:  
                data = choice_task()  
                if not data or data=='exit':  
                    break  
                print 'Send task',data
                client.send(str(data))  
                data = client.recv(bufsize)  
                if not data:  
                    break  
                print data.strip()  
            except:
                traceback.print_exc()
                break
            
        client.close() 

     
if __name__ == '__main__':
    for i in range(1) :
        t = Client()
        t.start()
        time.sleep(rate)