# -*- coding:utf-8 -*-

from termcolor import cprint

class Console() :
    def __init__( self ):
        pass

    def Assert( self, msg ):
        cprint( msg, 'magenta' )

    def Error( self, msg ):
        cprint( msg, 'red' )

    def Warning( self, msg ):
        cprint( msg, 'yellow' )

    def Debug( self, msg ):
        cprint( msg, 'white' )

    def Info( self, msg ):
        cprint( msg, 'green' )

    def Verbose( self, msg ):
        cprint( msg, 'cyan' )

