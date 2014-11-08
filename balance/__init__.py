from Balance import  *

if __name__=="__main__":
    host = ""
    port = 8080
    addr = (host, port)
    UDP = GetServerInfo()
    UDP.start()
    balance = ThreadingTCPServer(addr, TCP_Balance)
    balance.serve_forever()  