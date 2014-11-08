# -*- coding:utf-8 -*-  
#author: luoding
import socket
import threading
import time
import sys
from SocketServer import *   
import traceback 
import random
import hashlib

heartDict = {}
ServerList = {}

class ServerInfo:
    """
    节点服务器状态相关数据结构
    """
    def __init__(self, ip, cpu = 1, task = 1, state = -1): 
        self.ip = ip     
        self.cpu = cpu
        self.task = task
        self.weight = self.cpu * self.task #权值定义为CPU占用率与任务数之积
        self.state = state  #服务器状态，0为挂起，1为正常 -1 is waiting 
        
    def updateWeight(self):
        self.weight = int(self.cpu) * int(self.task)
        
    def updateCpu(self,cpu):
        self.cpu = int(cpu)
        self.updateWeight()  
        
    def updateTask(self,task):
        self.task = int(task)
        self.updateWeight() 
        
    def returnInfo(self):
        return (self.ip, self.cpu, self.task, self.state)
    


class LogSystem:
    """
    记录负载均衡操作到日志文件
    """ 
    def readLog(self,file_name):
        f = open(file_name)
        lines = f.readlines()
        for line in lines:
            print line 
        f.close()
        
    def readLogFromMySQL(self):
        pass      
        
    def writeLog(self, log, file_name):
        f = open(file_name, 'a') 
        f.write('%s : %s \n' % (time.strftime("%Y-%m-%d %H:%M:%S"),log))
        f.close()

    def writeLogToMySQL(self, log):
        pass
    
    def clearLog(self, file_name):
        f = open(file_name, 'w') 
        f.write('')
        f.close()


class HeartBeat(threading.Thread):  
    """
    心跳包处理，单独进程，与GetServerInfo配合使用
    发现节点服务器超过CHECK_TIMEOUT时间没有心跳包则挂起服务器
    CHECK_RATE为检查频率
    """
    def __init__(self):
        threading.Thread.__init__(self) 
        self.CHECK_TIMEOUT = 2 
        self.CHECK_RATE = 2
        self.log = LogSystem()
    
    def getServerName(self, ip):
        global ServerList
        for i in ServerList:
            if ServerList[i].ip == ip:
                return i
            
    def getSilent(self):
        """
        检测超时节点服务器，如有则返回服务器名，
        """
        nowTime = time.time()
        for key in heartDict:
            try:
                difference = nowTime - heartDict[key]
    
                if( difference - self.CHECK_TIMEOUT )>0:
                    name = self.getServerName(key)
                    return name
            except:
                break
        return 0

        
    def run(self):
        global ServerList
        print ' HeartBeat run'
        self.log.writeLog(' HeartBeat run','system_log.txt')
        while True:
            ret =  self.getSilent()
            if ret != 0:
                ServerList[ret].state = 0
                print 'server',ret,' is dead'
                self.log.writeLog('server %s is dead'% ret,'heartBeat_log.txt')
                        
            time.sleep(self.CHECK_RATE)
  
            
class GetServerInfo(threading.Thread):
    """
    UDP服务器，接收来自节点服务器的心跳包
    心跳包包含节点服务器当前CPU使用率
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.HOST = ''
        self.PORT = 8000
        self.BUFSIZE = 1024
        self.ADDR = (self.HOST, self.PORT)
        self.log = LogSystem()
        
    def getServerName(self, ip):
        global ServerList
        for i in ServerList:
            if ServerList[i].ip == ip:
                return i
    
    def findExist(self, ip):
        for key in ServerList:
            if ServerList[key].ip == ip:
                return 1;
        return 0;
            
    def firstBeat(self, ip):
        ServerName = 'Server'+str(len(ServerList))
        ServerList[ServerName] = ServerInfo(ip)
    
    def run(self):
        print ' UDP Server run'
        self.log.writeLog(' UDP Server run','system_log.txt') 
        udpSerSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        udpSerSock.bind(self.ADDR)
        #UDP服务器启动同时启动心跳包处理线程
        beat = HeartBeat()
        beat.start()
        
        while True:
            global ServerList
            #print 'waiting for server information..'
            cpu, addr = udpSerSock.recvfrom(self.BUFSIZE)
            global heartDict
            heartDict[addr[0]] = time.time()
            print 'get UDP information from',addr[0],',CPU Usage:',cpu
            self.log.writeLog('get UDP information from'+addr[0]+',CPU Usage:'+cpu, 'system_log.txt')
            
            if self.findExist(addr[0]) == 0:
                self.firstBeat(addr[0])
            
            ServerName = self.getServerName(addr[0])
            ServerList[ServerName].cpu = cpu
            print ServerName,'now cpu',ServerList[ServerName].cpu
            
            

class TCP_Balance(BaseRequestHandler):
    """
    负载均衡主程序，负责接收转发负载任务、负载算法
    """         
    def getBestOne(self):
        """
        根据算法返回当前权值最小的节点服务器IP
        """
        self.log = LogSystem()
        self.minOne = 9999999
        global ServerList
        
        for key in ServerList:
            ServerList[key].updateWeight()
            from __builtin__ import str
            self.log.writeLog('Name: '+key+'\t| cpu: '+str(ServerList[key].cpu)+'\t| task: '+str(ServerList[key].task)+'\t| weight: '+str(ServerList[key].weight)+'\t|state: '+str(ServerList[key].state),'Server_log.txt')
            print key,'cpu',ServerList[key].cpu
            print key,'task',ServerList[key].task
            print key,'weight',ServerList[key].weight
            print key,'state',ServerList[key].state
            
        for self.List in ServerList:
            if (ServerList[self.List].weight <  self.minOne) and (ServerList[self.List].state == 1):
                self.minOne = ServerList[self.List].weight 
                BestOne = self.List
                
        print 'Get BestOne',BestOne                
        return (ServerList[BestOne].ip, BestOne)
    
    def getCpuAvg(self):
        self.cpuTotal = 0;
        for key in ServerList:
            self.cpuTotal += int(ServerList[key].cpu)
        return self.cpuTotal/len(ServerList)
    
    def powerManage(self):
        print 'getCpuAvg',self.getCpuAvg()
        print 'ServerList Len',len(ServerList)
            
        if( self.getCpuAvg() >= 10 ):
            print "change"
            self.flag = 0
            for key in ServerList:
                if(self.flag == 0):
                    ServerList[key].state = 1
                if ((ServerList[key].state == -1)  and (self.flag > 0)):
                    ServerList[key].state = 1
                    return
                self.flag += 1
                
        else:
            self.flag = 0
            for key in ServerList:
                if(self.flag == 0):
                    ServerList[key].state = 1
                if ((ServerList[key].state == 1) and (self.flag > 0)):
                    ServerList[key].state = -1
                    return
                self.flag += 1
                
        if(len(ServerList) > 0):
            ServerList['Server0'].state = 1;
            print ServerList['Server0'].state
                
                
    def handle(self):
        self.log = LogSystem()  
        
        try:
            global ServerList
            data = self.request.recv(1024).strip()  
            task_name =  hashlib.md5(str(random.random() + time.time())).hexdigest()
            print 'receive task : '+task_name+' from '+self.client_address[0]
            self.log.writeLog('receive task  : '+task_name+' from '+self.client_address[0],'task_log.txt')
            self.powerManage()
            addr = self.getBestOne()
            task = (data, task_name, self.client_address[0], addr[0])

            ServerList[addr[1]].task += 1
            receive = self.client(addr[0], task)
            
            print 'send task ',task[1],'from'+task[2]+'to server',task[3]

            self.request.send(receive) 
            ServerList[addr[1]].task -= 1
            print 'return task  : '+task[1]+' to '+task[2]
            self.log.writeLog('return task  : '+task[1]+' to '+task[2],'task_log.txt')
        except:  
            traceback.print_exc()  
            
    def client (self,host,data):
        port = 9000
        bufsize = 1024
        ADDR = (host, port)
        print 'client addr ',ADDR
        tcpCliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpCliSock.connect(ADDR)
        
        tcpCliSock.send(data[0])
        print 'send data',data[0]
        receive = tcpCliSock.recv(bufsize)
        print 'receive data',receive
        return receive
        
        tcpCliSock.close()




 
    


        

