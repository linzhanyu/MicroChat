# -*- coding:utf-8 -*-

import sys
from ctypes import *

class COORD( Structure ):
    _fields_ = [("X", c_short),
                ("Y", c_short),
                ]

class SMALL_RECT( Structure ):
    _fields_ = [("Left", c_short),
                ("Top", c_short),
                ("Right", c_short),
                ("Bottom", c_short),
                ]


class SCREEN_BUFFER_INFO( Structure ):
    _fields_ = [("dwSize", COORD),
                ("dwCursorPosition", COORD),
                ("wAttributes", c_ushort),
                ("srWindow", SMALL_RECT),
                ("dwMaximumWindowSize", COORD),
                ]


class Console() :

    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE = -11
    STD_ERROR_HANDLE = -12

    GENERIC_READ = 0x80000000
    GENERIC_WRITE= 0x40000000

    FILE_SHARE_READ = 0x00000001
    FILE_SHARE_WRITE= 0x00000002

    CONSOLE_TEXTMODE_BUFFER = 1

    # Windows CMD命令行 字体颜色定义 text colors
    FOREGROUND_BLACK = 0x00 # black.
    FOREGROUND_DARKBLUE = 0x01 # dark blue.
    FOREGROUND_DARKGREEN = 0x02 # dark green.
    FOREGROUND_DARKSKYBLUE = 0x03 # dark skyblue.
    FOREGROUND_DARKRED = 0x04 # dark red.
    FOREGROUND_DARKPINK = 0x05 # dark pink.
    FOREGROUND_DARKYELLOW = 0x06 # dark yellow.
    FOREGROUND_DARKWHITE = 0x07 # dark white.
    FOREGROUND_DARKGRAY = 0x08 # dark gray.
    FOREGROUND_BLUE = 0x09 # blue.
    FOREGROUND_GREEN = 0x0a # green.
    FOREGROUND_SKYBLUE = 0x0b # skyblue.
    FOREGROUND_RED = 0x0c # red.
    FOREGROUND_PINK = 0x0d # pink.
    FOREGROUND_YELLOW = 0x0e # yellow.
    FOREGROUND_WHITE = 0x0f # white.
     
    # Windows CMD命令行 背景颜色定义 background colors
    BACKGROUND_BLUE = 0x10 # dark blue.
    BACKGROUND_GREEN = 0x20 # dark green.
    BACKGROUND_DARKSKYBLUE = 0x30 # dark skyblue.
    BACKGROUND_DARKRED = 0x40 # dark red.
    BACKGROUND_DARKPINK = 0x50 # dark pink.
    BACKGROUND_DARKYELLOW = 0x60 # dark yellow.
    BACKGROUND_DARKWHITE = 0x70 # dark white.
    BACKGROUND_DARKGRAY = 0x80 # dark gray.
    BACKGROUND_BLUE = 0x90 # blue.
    BACKGROUND_GREEN = 0xa0 # green.
    BACKGROUND_SKYBLUE = 0xb0 # skyblue.
    BACKGROUND_RED = 0xc0 # red.
    BACKGROUND_PINK = 0xd0 # pink.
    BACKGROUND_YELLOW = 0xe0 # yellow.
    BACKGROUND_WHITE = 0xf0 # white.

    def __init__( self ) :
        self.std_out_handle = windll.kernel32.GetStdHandle(Console.STD_OUTPUT_HANDLE)
        info = SCREEN_BUFFER_INFO()
        windll.kernel32.GetConsoleScreenBufferInfo( self.std_out_handle, pointer(info) )
        self.std_out_color = info.wAttributes
        # print( '原始的颜色值 : 0x%02X' % (info.wAttributes, ) )
        # self.std_out_color = Console.FOREGROUND_DARKWHITE 
        # print( '原始的颜色值 : 0x%02X' % (self.std_out_color, ) )

    def Title( self, title ):
        windll.kernel32.SetConsoleTitleW( title )

    def SetOutputCodepage( self, cp ):
        cp = windll.kernel32.GetConsoleOutputCP()
        print('Codepage : %d' % (cp, ))
        return 0 != windll.kernel32.SetConsoleOutputCP( cp )

    def clear( self ):
        info = SCREEN_BUFFER_INFO()
        windll.kernel32.GetConsoleScreenBufferInfo( self.std_out_handle, pointer(info) )
        conSize = info.dwSize.X * info.dwSize.Y;
        coord = COORD()
        written = c_uint()
        windll.kernel32.FillConsoleOutputCharacterW( self.std_out_handle, c_wchar(' '), conSize, coord, pointer(written) )
        # windll.kernel32.FillConsoleOutputAttribute( self.std_out_handle, info.wAttributes, conSize, coord, pointer(written) )
        windll.kernel32.SetConsoleCursorPosition( self.std_out_handle, coord )

    # ============================================================
    # 颜色控制
    # ============================================================
    def set_text_color( self, color ):
        ret = windll.kernel32.SetConsoleTextAttribute( self.std_out_handle, color )
        return ret

    def resetColor( self ):
        self.set_text_color( self.std_out_color )

    def __color_msg( self, color, msg ):
        self.set_text_color( color )
        try:
            # msg = msg.encode( 'UTF-8' )
            # rawOut = open(1, 'wb', closefd=False)
            # rawOut.write( msg )
            # rawOut.flush()
            # rawOut.close()
            sys.stdout.write( str(msg) + '\n' )
        except UnicodeEncodeError as e:
            pass
        self.resetColor()

    def test_color( self, msg ):
        self.__color_msg( Console.FOREGROUND_BLACK, msg )
        self.__color_msg( Console.FOREGROUND_DARKBLUE, msg )
        self.__color_msg( Console.FOREGROUND_DARKGREEN, msg )
        self.__color_msg( Console.FOREGROUND_DARKSKYBLUE, msg )
        self.__color_msg( Console.FOREGROUND_DARKRED, msg )
        self.__color_msg( Console.FOREGROUND_DARKPINK, msg )
        self.__color_msg( Console.FOREGROUND_DARKYELLOW, msg )
        self.__color_msg( Console.FOREGROUND_DARKWHITE, msg )
        self.__color_msg( Console.FOREGROUND_DARKGRAY, msg )
        self.__color_msg( Console.FOREGROUND_BLUE, msg )
        self.__color_msg( Console.FOREGROUND_GREEN, msg )
        self.__color_msg( Console.FOREGROUND_SKYBLUE, msg )
        self.__color_msg( Console.FOREGROUND_RED, msg )
        self.__color_msg( Console.FOREGROUND_PINK, msg )
        self.__color_msg( Console.FOREGROUND_YELLOW, msg )
        self.__color_msg( Console.FOREGROUND_WHITE, msg )

    def Assert( self, msg ):
        self.__color_msg( Console.FOREGROUND_PINK, msg )

    def Error( self, msg ):
        self.__color_msg( Console.FOREGROUND_RED, msg )

    def Warning( self, msg ):
        self.__color_msg( Console.FOREGROUND_YELLOW, msg )

    def Debug( self, msg ):
        self.__color_msg( Console.FOREGROUND_WHITE, msg )

    def Info( self, msg ):
        self.__color_msg( Console.FOREGROUND_GREEN, msg )

    def Verbose( self, msg ):
        self.__color_msg( Console.FOREGROUND_DARKYELLOW, msg )


