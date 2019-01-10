# -*- coding:utf-8 -*-

# 日志管理器单件 2012-01-26
# from utile.singleton import Singleton
from singleton import Singleton
import unittest

g_log = None

class LogMng( Singleton ):
    _logging = None
    def initlog( self, filename ):
        if LogMng._logging is None :
            import logging
            LogMng._logging = logging
        # FORMAT = '%(asctime)-15s %(name)s %(message)s'
        FORMAT = u'%(asctime)-15s %(levelname)s %(message)s'
        # logging.basicConfig(filename='fms.log', format=FORMAT, level=logging.INFO)
        # 每一次都清空原有的日志历史
        self.hdlr = self._logging.FileHandler(filename, 'w')
        self.fmtter = self._logging.Formatter( FORMAT )
        self.hdlr.setFormatter( self.fmtter )
        self.logger = self._logging.getLogger()
        self.logger.addHandler( self.hdlr )
        self.hdlr.setLevel( self._logging.NOTSET )
        self.logger.setLevel( self._logging.NOTSET )
        import sys
        if sys.version_info < (3, 0):
            sys.stdout = log_out()
            sys.stderr = log_out()
        return self.logger

    def AddHandler( self, handler ):
        hdlr = handler
        hdlr.setFormatter( self.fmtter )
        hdlr.setLevel( self._logging.INFO )
        self.logger.addHandler( hdlr )

    def RemoveHandler( self, handler ):
        self.logger.removeHandler( handler )

    def finilog( self ):
        if LogMng._logging is None :
            return
        # logging = LogMng._logging
        self.logger.removeHandler( self.hdlr )
        self.hdlr.flush()
        self.hdlr.close()

    def debug( self, *args ):
        if LogMng._logging is None :
            return
        self.logger.debug( *args )

    def info( self, *args ):
        if LogMng._logging is None :
            return
        self.logger.info( *args )

    def warning( self, *args ):
        if LogMng._logging is None :
            return
        self.logger.warning( *args )

    def error( self, *args ):
        if LogMng._logging is None :
            return
        self.logger.error( *args )

    def write( self, string ):
        self.hdlr.emit( string )

def LOG_DEBUG( *args ):
    LogMng().debug( *args )

def LOG_INFO( *args ):
    LogMng().info( *args )

def LOG_WARNING( *args ):
    LogMng().warning( *args )

def LOG_ERROR( *args ):
    LogMng().error( *args )

class log_out():
    def write( self, s ):
        # s = s.replace( u'\r', u'' )
        # s = s.replace( u'\n', u'' )
        if s is None :
            return

        if len(s) > 0 :
            LOG_DEBUG( s )
        
class TestCaseFmsLog( unittest.TestCase ):
    def setUp( self ):
        LogMng().initlog('test.log')

    def tearDown( self ):
        LogMng().finilog()

    def testLogDebug( self ):
        LOG_DEBUG( 'TestCase debug log.' )

    def testLogInfo( self ):
        LOG_INFO( 'TestCase info log.' )

    def testLogWarning( self ):
        LOG_WARNING( 'TestCase warning log.' )

    def testLogError( self ):
        LOG_ERROR( 'TestCase error log.' )

def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestCaseFmsLog('testLogDebug'))
    suite.addTest(TestCaseFmsLog('testLogInfo'))
    suite.addTest(TestCaseFmsLog('testLogWarning'))
    suite.addTest(TestCaseFmsLog('testLogError'))
    return suite

if __name__ == '__main__':
    unittest.main()


