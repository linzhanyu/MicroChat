# -*- coding:utf-8 -*-

# Python 单件实现
# 有需要使用单件的,从这个类继承一个就OK

# 所有继承自 Singleton 的类都小心 __init__ 函数的多次调用情况

import threading, os

class Singleton( object ):
    objs = {}
    objs_locker = threading.Lock()

    def __new__(cls, *args, **kv):
        # if cls in cls.objs:
        #     return cls.objs[cls]
        cls.objs_locker.acquire()
        try:
            if cls in cls.objs:
                return cls.objs[cls]
            # print( 'NEW ', cls )
            cls.objs[cls] = object.__new__(cls)
        finally:
            cls.objs_locker.release()
            return cls.objs[cls]

class Singleton2(type):  
    _instances = {}
    def __init__(cls, name, bases, dict):  
        super(Singleton2, cls).__init__(name, bases, dict)  

    def __call__(cls, *args, **kw):  
        pid = os.getpid()
        if pid not in cls._instances:
            cls._instances[pid] = {}
        pInsts = cls._instances[pid]
        if cls not in pInsts:
            pInsts[ cls ] = super(Singleton2, cls).__call__(*args, **kw)  
        return pInsts[ cls ]  

instances = {}
def Singleton3( cls, *args, **kw ):
    def _singleton(*args, **kw):
        pid = os.getpid()
        if pid not in instances:
            instances[pid] = {}
        pInsts = instances[pid]
        if cls not in pInsts:
            pInsts[cls] = cls(*args, **kw)
        return pInsts[cls]
    return _singleton
