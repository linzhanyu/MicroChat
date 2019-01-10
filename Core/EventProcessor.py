# -*- coding:utf-8 -*-
from LogicEvent import ThreadEvt
from AdvTask import ThreadSafe
from config import BackTestConfig as btCfg
from queue import Queue, Empty
from threading import Thread, get_ident, Event, Lock
import time, os

# 功能 把事件分发器中的事件收集到本线程队列中进行二次分发
class ThreadEventProcessor:
    def __init__( self, btMngr ):
        self.__tid = get_ident()
        self._mng = btMngr
        self.__event = Event()
        self.__lock  = Lock()
        self.__queue = Queue()
        self.__active = False
        self.__wait = False
        if False and btCfg.profile :
            self.__thread = Thread( target = self.__EntryProfile )
        else:
            self.__thread = Thread( target = self._Entry )
        self.__handlers = []
        for i in range(ThreadEvt.COUNT):
            self.__handlers.append( [] )
        # print( os.getpid(), self.__thread.ident, id(self.__queue) )
        # print( 'PID:%X QID:%X' % (os.getpid(), id(self.__queue) ) )

    def RegEvt( self, evt, handler ):
        # 通过该接口注册的事件会在当前线程中执行
        if handler not in self.__handlers[evt]:
            self.__handlers[evt].append( handler )
            # print( 'RegEvt :', evt )

        self._mng.evtMng.Register( evt, self.Retrieve )

    def UnRegEvt( self, evt, handler ):
        if handler in self.__handlers[evt]:
            self.__handlers[evt].remove( handler )
            # print( 'UnRegEvt :', evt )
        empty = len( self.__handlers[evt] ) == 0
        if empty:
            self._mng.evtMng.UnRegister( evt, self.Retrieve )

    def Retrieve( self, evt, *args, **kw ):
        # 回收线程事件等待线程处理
        # print( '%X -> %X Retrieve: %d' % (get_ident(), self.__thread.ident, evt) )
        def __PostEvent( event, *args, **kw ):
            self.__queue.put( (event, args, kw) )
            self.__event.set()
        ThreadSafe.SafeAccess( self.__lock, lambda : __PostEvent( evt, *args, **kw ) )

    def ThreadRun( self ):
        self.__active = True
        if not self.__thread.is_alive():
            self.__thread.start()
            # print( 'PID:0x%X - Start Thread: 0x%X -- run --> 0x%X %s' % (os.getpid(), get_ident(), self.__thread.ident, self.__class__.__name__, ) )

    def ThreadStop( self ):
        # print( 'ThreadStop . %X' % ( self.__thread.ident, ) )
        self.__active = False
        self.__wait = False
        # while self.__thread.is_alive():
        #     self.__thread.join( timeout = 0.001 )
        #     # print( 'Wait thread : ', self.__thread.is_alive() )

    def __EntryProfile( self ):
        import cProfile, pstats, os
        from config import Config
        filename = os.path.join( Config.dataDir, 'profile_%s_%08X' % (__name__, os.getpid(), ) )
        cProfile.runctx( 'self._Entry()', globals(), locals(), filename )
        p = pstats.Stats( filename )
        p.strip_dirs().sort_stats('tottime', 'cumulative').print_stats( 10 )

    def _Entry( self ):
        ''' 线程入口点 派生类应该重写该方法 '''
        raise NotImplementedError

    def __GetEvent(self):
        if self.__queue.qsize() > 0:
            return self.__queue.get( block=False, timeout=None )

    def __ClearEvent(self):
        if self.__queue.empty():
            self.__event.clear()

    def _Loop( self ):
        ''' 进入事件循环 '''

        while self.__active:
            # print( '0', end='' )
            if self.__event.is_set():
                try:
                    # print( self.__active and '1' or '0', end='' )
                    event = ThreadSafe.SafeAccess( self.__lock, lambda : self.__GetEvent() )
                    # event = self.__queue.get( block = False, timeout = None )
                    # event = self.__queue.get_nowait()
                    self.__Dispatch( event )
                    # print( '2', end='' )
                    ThreadSafe.SafeAccess( self.__lock, lambda : self.__ClearEvent() )

                    # if self.__queue.empty():
                    #     self.__event.clear()
                    # print( '3', end='' )
                except Empty:
                    time.sleep(0.01)
                    # pass
            else:
                # print( '.', end='' )
                time.sleep(0.01)
                # pass
        # print( 'Thread Loop Exit.', self.__class__.__name__ )

    def _WaitForEvt( self, event ):
        # 陷入 Wait 循环事件处理
        self.__wait = True
        self.RegEvt( event, self.__UntilEvt )

        while self.__wait:
            if self.__event.is_set():
                try:
                    evt = ThreadSafe.SafeAccess( self.__lock, lambda : self.__queue.get( block=False, timeout=None ) )
                    # evt = self.__queue.get( block = False, timeout = 0.01 )
                    self.__Dispatch( evt )
                    ThreadSafe.SafeAccess( self.__lock, lambda : self.__ClearEvent() )
                    # if self.__queue.empty():
                    #     self.__event.clear()
                except Empty:
                    time.sleep(0.01)
                    # pass
            else:
                time.sleep(0.01)
                # pass
        self.UnRegEvt( event, self.__UntilEvt )

    def __UntilEvt( self, evt ):
        # 退出 Wait 循环事件处理
        self.__wait = False

    def __Dispatch( self, event ):
        threadEvt, args, kw = event
        if threadEvt >= ThreadEvt.COUNT:
            raise TypeError( 'Unknow event : %d' % threadEvt )

        handlerList = self.__handlers[ threadEvt ]
        # print( '%X' % (self.__thread.ident), 'ThreadEvt : ', threadEvt, args, kw )
        for handler in handlerList:
            handler( threadEvt, *args, **kw )

