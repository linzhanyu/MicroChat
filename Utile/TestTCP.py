# -*- coding:utf-8 -*-

from Server import ThreadedTCPServer, MyThreads, ThreadedTCPRequestHandler
from Client import ThreadedTCPClient
import time, threading

HOST, PORT = 'localhost', 40000

server = None
clientThread = None

def StartTCPServer():
    global server
    server = ThreadedTCPServer( (HOST, PORT), ThreadedTCPRequestHandler )
    serverThread = threading.Thread(target=server.serve_forever)
    serverThread.daemon = True
    serverThread.start()

def StartTCPClient():
    global clientThread
    clientThread = ThreadedTCPClient( (HOST, PORT) )
    clientThread.daemon = True
    clientThread.start()

class Test001():
    @staticmethod
    def TestStaticFunc():
        print( 'Test001.TestStaticFunc' )

class Test002():
    @staticmethod
    def TestStaticFunc():
        print( 'Test002.TestStaticFunc' )


if __name__ == '__main__':
    StartTCPServer()
    StartTCPClient()
    # time.sleep(60.0)
    StartTCPClient()
    StartTCPClient()

    Test001.TestStaticFunc()
    Test002.TestStaticFunc()

    try:
        while True:
            time.sleep(10.0)
    except KeyboardInterrupt as e :
        pass

    finally:
        print( 'Clear / Quit.' )
        server.shutdown()
        server.server_close()
        del clientThread


