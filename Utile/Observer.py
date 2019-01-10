# -*- coding:utf-8 -*-
# Observer 模式实现 [线程安全]

from __future__ import print_function
import threading, sys

class Subject() :
    '''话题'''
    def __init__(self):
        # 线程不安全
        # 如果是多线程之间的 ob 需要有一个列表，然后在另一个中取
        self.__lock = threading.Lock()
        self.__obs = set()

    def __Lock( self, func ):
        if func is not None:
            self.__lock.acquire()
            func()
            self.__lock.release()

    def Register( self, observer ):
        if observer is None:
            return False

        # print( 'Reg:', id(observer), observer )
        if observer not in self.__obs:
            func = lambda : self.__obs.add(observer)
            self.__Lock( func )
            return True
        return False

    def Unregister( self, observer ):
        if observer is None:
            return False

        if observer in self.__obs:
            func = lambda : self.__obs.remove(observer)
            self.__Lock( func )
            return True
        return False

    def IsRegistered( self, observer ):
        return observer in self.__obs

    def Notify( self, evtId, *params ):
        def notify():
            # [::-1] 倒序是解决循环中删除元素最简单的方法，数据多时效率上不如 filter
            for ob in list(self.__obs)[::-1]:
                ob.OnNotify( evtId, *params )
        self.__Lock( notify )


class Observer():
    '''观察者'''
    def __init__(self):
        self.__dict = {}

    def BindEvt(self, evtId, func):
        if func == None:
            return

        # print( 'BindEvt : ', evtId, func )
        if evtId in self.__dict:
            # 事件处理函数不要重复注册
            if func not in self.__dict[evtId]:
                self.__dict[evtId].add(func)
        else:
            self.__dict[evtId] = set([func,])

    def UnbindEvt(self, evtId, func):
        # print( 'UnbindEvt : ', evtId, func, dir(func) )
        if evtId in self.__dict:
            funcs = self.__dict[evtId]
            if func in funcs:
                funcs.remove(func)
                # print(type(funcs))
                if len(funcs) == 0:
                    del self.__dict[evtId]

    def OnNotify(self, evtId, *params):
        if evtId in self.__dict:
            funcs = self.__dict[evtId]
            # print(type(funcs))
            for func in list(funcs)[::-1]:
                func( *params )
            # print( len(funcs) )

# if __name__ == '__main__':
#     s = Subject()
#     o = Observer()
#     
#     n = 10
#     view = lambda *params : o.UnbindEvt(0, view)
#     viewers = (view,)*n
#     # viewers = (lambda *params : print(sys._getframe().f_code),)*n
#     for i, viewer in enumerate(viewers):
#         o.BindEvt( i, viewer )
# 
#     viewers = (lambda *params : print('OK! ', *params),)*n
#     for i, viewer in enumerate(viewers):
#         o.BindEvt( i, viewer )
# 
#     s.Register(o)
#     s.Notify(0, None)
#     s.Notify(0, None)
#     s.Unregister(o)
#     pass

