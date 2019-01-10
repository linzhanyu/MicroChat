# -*- coding:utf-8 -*-

import threading
import socket
from multiprocessing import cpu_count

# test
from NetMsg import *

class ThreadedTCPClient( threading.Thread ):
    def __init__( self, address ) :
        threading.Thread.__init__( self )
        self.client = None
        self.address = address
        self.rawbuf = None
        InitMsg()

    def run( self ):
        if self.client == None :
            # self.client = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            # self.client.connect( self.address )
            self.client = TCPClient( self.address )
            self.client.Connect()
            msg = BMMsgRegistBuildServer()
            msg.SetAttribute( 'Android', 'Windows', cpu_count(), '1.0' )
            self.client.SendNetMsg( msg )

class TCPClient() :
    def __init__( self, address ) :
        self.s = None
        self.address = address

    def Connect( self ):
        if self.s == None :
            self.s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            # self.s.bind(('localhost', 7722))
            self.s.connect( self.address )

    def Disconnect( self ):
        if self.s is not None :
            # self.s.shutdown( socket.SHUT_RDWR )
            self.s.close()

    def SendNetMsg( self, msg ):
        if self.s is None:
            return False

        self.s.send( msg.Pack() )

    def RecvNetMsg( self ) :
        if self.s is None:
            return None

        msg = None
        while( msg == None ) :
            raw = self.s.recv( 1024 )
            self.rawbuf += raw
            msg, l = NetMsg.Unpack( self.rawbuf )
        self.rawbuf = self.rawbuf[l:]
        return msg


