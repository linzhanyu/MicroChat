# -*- coding:utf-8 -*-

from __future__ import print_function
import os, sys, getopt
import unittest

__DEBUG = False

def init_path():
    curdir = os.getcwd()
    sys.path.append( curdir )
    sys.path.append( os.path.join( curdir, 'Utile' ) )
    sys.path.append( os.path.join( curdir, 'Core' ) )
    sys.path.append( os.path.join( curdir, 'UI' ) )


def usage():
    helpStr = '''
    python3 Main.pyw --unittest
    '''

    print( helpStr )

def main( argv ):
    # print('start')
    init_debug()
    init_path()

    bConsole = False

    try :
        opts, args = getopt.getopt( argv, 'ch', ['help', 'unittest', 'console', ] )
    except getopt.GetoptError :
        usage()
        sys.exit(2)

    for opt, arg in opts:
        # print('hello')
        print( arg )
        if opt in ( '-h', '--help', ) :
            usage()
            sys.exit()
        elif opt in ( '--unittest', ):
            # unittest.main( exit=True )
            unittest_main( bConsole )
            sys.exit('...')
        elif opt in ( '-c', '--console', ) :
            bConsole = True

    init_log()
    application_main( bConsole )
    fini_log()

def init_debug():
    if __DEBUG :
        import pdb
        pdb.set_trace()

def init_log():
    import logmng
    from config import Config
    # print( type(Config.LogFile) )
    # raise 0
    log = logmng.LogMng()
    log.initlog( Config.LogFile )
    logmng.g_log = log

def fini_log():
    import logmng
    log = logmng.LogMng()
    log.finilog()
    logmng.g_log = None

def application_main( console ):
    from Core import MainApp
    MainApp.Run( console )

def unittest_main( console ):
    print( 'unittest mode.' )

    # 以代码引用结构来运行 UnitTest
    from Core import MainApp
    from Core import Calendar
    suite = MainApp.suite()
    runner = unittest.TextTestRunner()
    runner.run( suite )
    print( 'unittest finish' )

    # # import ftp_transfer
    # # import logmng
    # from Core import TaskBuildMini
    # from Core import VerControl
    # # suite_version = VersionControl.suite()
    # # suite_autoupdate = AutoUpdate.suite()
    # # suite_server = MainServer.suite()
    # # suite_server = BuildServer.suite()
    # suite_core = TaskBuildMini.suite()
    # suite_version = VerControl.suite()
    # alltests = unittest.TestSuite( (suite_core, suite_version) )
    # runner = unittest.TextTestRunner()
    # runner.run( alltests )

# def TestCandlesTick():
#     from sqlalchemy import create_engine
#     import numpy as np
#     import pandas as pd
#     import matplotlib.pyplot as plt
#     import matplotlib.finance as f
# 
#     engine = create_engine('mysql+mysqldb://root:@localhost/finance?charset=utf8')
#     print( 'begin.' )
#     with engine.connect() as conn, conn.begin():
#         # ''
#         df = pd.read_sql('SELECT date, open, high, low, close, volume FROM 60minute WHERE code=002624', conn)
#         df = df[-100:]
#         df.reset_index()
#         df.set_index('date')
#         print( len(df) )
#         v = df.head(5)
#         print(v)
#         # n_groups = 5
#         # index = np.arange(n_groups)
#         # print(index)
#         fig, ax = plt.subplots()
#         # rects1 = f.candlestick2_ochl(ax, v.open, v.close, v.high, v.low, colorup='r', colordown='g' )
#         quotes = [[0, v.open, v.high, v.low, v.close] for k, v in df.iterrows()]
#         idx = 0
#         for item in quotes:
#             item[0] = idx * 0.25 + 0.1
#             idx += 1
# 
#         f.candlestick_ohlc(ax, quotes, width=0.6)
#         # ax.xaxis_date()
#         # ax.autoscale_view()
#         plt.show()


if __name__ == '__main__':
    main( sys.argv[1:] )
    # init_path()
    # unittest_main( True )
    # print( 'main exit.' )


