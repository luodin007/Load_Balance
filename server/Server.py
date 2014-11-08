'''
Created on Jun 10, 2014

@author: luoding
'''
import time
from SocketServer import *
import traceback
import UDP_Server

class process:
    def run(self, taskNum):
	print 'taskNum',taskNum
	if(taskNum == '1'):
	    self.task1()
	elif(taskNum == '2'):
	    self.task2()
	elif(taskNum == '3'):
	    self.task3()
	return taskNum
        
    def task1(self):
	print time.strftime("%Y-%m-%d %H:%M:%S"),'start run task1'
        time.sleep(1)
	print time.strftime("%Y-%m-%d %H:%M:%S"),' run end task1'

    def task2(self):
	print time.strftime("%Y-%m-%d %H:%M:%S"),'start run task2'
        time.sleep(2)
	print time.strftime("%Y-%m-%d %H:%M:%S"),' run end task2'

    def task3(self):
	print time.strftime("%Y-%m-%d %H:%M:%S"),'start run task3'
        time.sleep(3)
	print time.strftime("%Y-%m-%d %H:%M:%S"),' run end task3'

       

class Server(BaseRequestHandler):  
    def handle(self):  
        try:
	    print time.strftime("%Y-%m-%d %H:%M:%S"),'get data'
            data = self.request.recv(1024).strip() 
            t = process()
            print time.strftime("%Y-%m-%d %H:%M:%S"),"receive from (%r): task%r" % (self.client_address, data)  
            receive = t.run(data)
            self.request.send(receive)
	    print time.strftime("%Y-%m-%d %H:%M:%S"),"return to (%r): task%r" % (self.client_address, receive)
        except:
            traceback.print_exc()
            
if __name__ == "__main__":  
    host = ""
    port = 9000  
    addr = (host, port) 
    udp = UDP_Server.UDP_Server()
    udp.start() 
    server = ThreadingTCPServer(addr, Server)  
    server.serve_forever()  
