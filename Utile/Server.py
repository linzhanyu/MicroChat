# -*- coding:utf-8 -*-

import socket
import threading
import socketserver
from NetMsg import *

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        print('a client connected.')
        self.rawbuf = b''
        msg = None
        while( msg == None ):
            rawData = self.request.recv(1024)
            self.rawbuf += rawData
            msg, l = NetMsg.Unpack( self.rawbuf )
        self.rawbuf = self.rawbuf[l:]
        # print( type(msg), msg.msgID, 'BuildType:'+msg.BuildType, 'Platform:'+msg.Platform, 'Process:'+msg.Processor )

        # data = 'Server - ' + str(self.request.recv(1024), 'ascii')
        # cur_thread = threading.current_thread()
        # response = bytes("{}: {}".format(cur_thread.name, data), 'ascii')
        # self.request.sendall(response)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class TCPServer:
    def __init__( self ):
        self.server = ThreadedTCPServer( (HOST, PORT), ThreadedTCPRequestHandler )

    def Start( self ):
        self.serverThread = threading.Thread(target=server.serve_forever)
        self.serverThread.daemon = True
        self.serverThread.start()

    def Close( self ):
        self.server.shutdown()
        self.server_close()






# TEST CODE
class MyThreads(threading.Thread):
    def __init__(self, address):
        threading.Thread.__init__(self)
        self.server = None
        self.address = address
        InitMsg()

    # def __del__(self):
    #     print( 'Delete server.' )
    #     if self.server is not None:
    #         self.server.shutdown()

    def run(self):
        if self.server == None:
            # address = ('localhost', 40000)
            self.server = socketserver.TCPServer(self.address, ThreadedTCPRequestHandler )

        self.server.serve_forever()

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(bytes(message, 'ascii'))
        response = str(sock.recv(1024), 'ascii')
        print("Received: {}".format(response))
    finally:
        sock.close()

if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 40000

    # server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    # ip, port = server.server_address

    # # Start a thread with the server -- that thread will then start one
    # # more thread for each request
    # server_thread = threading.Thread(target=server.serve_forever)
    # # Exit the server thread when the main thread terminates
    # server_thread.daemon = True
    # server_thread.start()
    t = MyThreads( (HOST, PORT) )
    t.setDaemon(True)
    t.start()

    # print("Server loop running in thread:", server_thread.name)

    # client(ip, port, "Hello World 1")
    # client(ip, port, "Hello World 2")
    # client(ip, port, "Hello World 3")
    client(HOST, PORT, "Hello World 1")
    client(HOST, PORT, "Hello World 2")
    client(HOST, PORT, "Hello World 3")

    # server.shutdown()
    del t

