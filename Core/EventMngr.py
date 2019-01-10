# -*- coding:utf-8 -*-

from MyEnum import Enum
from singleton import Singleton, Singleton2, Singleton3
from LogicEvent import ThreadEvt
from queue import Queue, Empty
from threading import Thread, Event, Lock, get_ident
from AdvTask import ThreadSafe
import time, os

@Singleton3
class EventMngr( object ):
    # __metaclass__ = Singleton2

    def __init__( self ):
        # 切记不要在这里写任何东西 Singleton 实现不完美
        # super( EventMngr, self ).__init__()
        pass

    def Init( self ):
        # 事件队列
        # print( 'EventMngr PID:0x%X ObjectID:0x%X' % (os.getpid(), id(self), ) )
        self.__event = Event()
        self.__lock  = Lock()
        self.__queue = Queue()
        # 事件分发处理
        self.__thread = Thread( target = self.__Run )
        # 激活线程
        self.__active = False

        # 事件专用处理器
        self.__handlers = [] * ThreadEvt.COUNT
        for i in range(ThreadEvt.COUNT):
            self.__handlers.append( [] )

        # 通用事件处理器
        self.__commonHandlers = []

    def Fini( self ):
        pass

    def Register( self, threadEvt, handler ):
        handlerList = self.__handlers[ threadEvt ]
        # print( len( self.__handlers ) )
        # print( 'Event %d -> Handler count :%d' % (threadEvt, len(handlerList), ) )
        if handler not in handlerList:
            handlerList.append( handler )
            # print( 'Register:', threadEvt )
        # print(
        #         len(self.__handlers[0]),
        #         len(self.__handlers[1]),
        #         len(self.__handlers[2]),
        #         len(self.__handlers[3]),
        #         len(self.__handlers[4]),
        #         len(self.__handlers[5]),
        #         len(self.__handlers[6]),
        #         len(self.__handlers[7]),
        #         )

    def UnRegister( self, threadEvt, handler ):
        handlerList = self.__handlers[ threadEvt ]
        if handler in handlerList:
            handlerList.remove( handler )
            # print( 'UnRegister:', threadEvt )

    def RegisterCommon( self, handler ):
        if handler not in self.__commonHandlers:
            self.__commonHandlers.append( handler )

    def UnRegisterCommon( self, handler ):
        if handler in self.__commonHandlers:
            self.__commonHandlers.remove( handler )

    def PostEvent( self, event, *args, **kw ):
        # print( '%X -> %X PostEvent: %d' % (get_ident(), self.__thread.ident, event) )
        def __PostEvent( event, *args, **kw ):
            self.__queue.put( (event, args, kw) )
            self.__event.set()

        ThreadSafe.SafeAccess( self.__lock, lambda : __PostEvent( event, *args, **kw ) )

        # print( self.__queue.qsize(), end='' )

    def __Run( self ):
        def ClearEvent():
            if self.__queue.empty():
                self.__event.clear()

        while self.__active :
            if self.__event.is_set():
                # pass
                try:
                    event = ThreadSafe.SafeAccess( self.__lock, lambda : self.__queue.get( block=False, timeout=None ) )
                    #if self.__lock.acquire():
                    #    event = self.__queue.get( block = False, timeout = 0.001 )
                    #    self.__lock.release()
                    self.__Dispatch( event )
                    ThreadSafe.SafeAccess( self.__lock, ClearEvent )
                    # if self.__queue.empty():
                    #     self.__event.clear()
                except Empty:
                    time.sleep(0)
                    # pass
            else:
                time.sleep(0)
                # pass
        # print( 'ThreadStop . %X' % ( get_ident(), ) )

    def __Dispatch( self, event ):
        threadEvt, args, kw = event
        if threadEvt < ThreadEvt.COUNT:
            handlerList = self.__handlers[ threadEvt ]
            # print( 'ThreadEvt : ', threadEvt, len(handlerList) )
            for handler in handlerList:
                handler( threadEvt, *args, **kw )

    def Start( self ):
        self.__active = True
        self.__thread.start()
        # print( 'PID:0x%X - Start Thread: 0x%X -- run --> 0x%X %s' % (os.getpid(), get_ident(), self.__thread.ident, self.__class__.__name__, ) )


    def Stop( self ):
        self.__active = False
        self.Join()

    def Join( self ):
        try:
            while self.__thread.is_alive():
                # print( 'TID : 0x%X' % (get_ident(), ) )
                self.__thread.join( timeout=0.1 )
        except RuntimeError:
            pass

eventMngr = None
eventMngr = EventMngr()

