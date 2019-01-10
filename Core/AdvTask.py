# -*- coding=utf-8 -*-
# 高级任务管理器 进程 线程 双管齐下
# 线程应对网络类 IO大 任务
# 进程应对计算密集型任务
# ============================================================
# 为任务发起线程提供任务缓存队列
# ============================================================

# from .Task import WorkerThread

import logmng
from config import Config
# from DataSource.Common import *

import multiprocessing
from multiprocessing.dummy import Pool as ThreadPool
import time, sys

class Task:
    pass

opQueue = lambda _queue, value : _queue.put( value )
opList  = lambda _list, value : _list.append( value )
opValue = lambda op : op( container, value )

def AppendValue( op, container, value ):
    op( container, value )


class ThreadSafe():

    @staticmethod
    def SafeAccess( lock, func ):
        try:
            lock.acquire()
            if func is not None:
                ret = func()
        finally:
            lock.release()
        return ret

    @staticmethod
    def SafePush( lock, container, value ):
        name = type(container).__name__
        op = None
        if 'Queue' in name:
            op = opQueue
        if 'List' in name:
            op = opList
        if op is None:
            raise Exception( 'Type %s does not support.' % ( name, ) )
        return ThreadSafe.SafeAccess( lock, lambda : op( container, value ) )

    @staticmethod
    def SafePop( lock, container, value ):
        name = type(container).__name__
        # print( name )
        if 'Queue' in name:
            op = lambda queue, value : queue.qsize() > 0 and queue.get() or None
        if 'List' in name:
            op = lambda _list, value : len(_list) > 0 and _list.pop(0) or None
        if op is None:
            raise Exception( 'Type %s does not support.' % ( name, ) )
        return ThreadSafe.SafeAccess( lock, lambda : op( container, value ) )

    # Dict
    @staticmethod
    def SafeSetValue( lock, dic, key, value ):
        def Operator() :
            dic[key] = value
        return ThreadSafe.SafeAccess( lock, lambda : Operator() )

    @staticmethod
    def SafeGetValue( lock, dic, key ):
        return ThreadSafe.SafeAccess( lock, lambda : dic[key] if key in dic else None )

    @staticmethod
    def SafeDelValue( lock, dic, key ):
        def Operator():
            if key in dic:
                del dic[key]
        return ThreadSafe.SafeAccess( lock, lambda : Operator()   )


class MultiTaskBase():
    __instance = None

    def __init__( self ):
        pass

    # def __AddThreadTask( self, func, params, callback ):
    #     ''' 添加线程任务 '''
    #     # 这些任务都是可能会推到其它进程中去跨进程执行的
    #     return None

    # def __AddProcessTask( self, func, params, callback ):
    #     # 这此任务是分配到其它进程中去执行的注意同步及参数传递
    #     return None

    def CreateTaskQueue( self ):
        ''' 创建任务列表 '''
        manager  = multiprocessing.Manager()
        self._taskQueue = manager.Queue()
        self._retQueue = manager.Queue()
        self._workerDict = manager.dict()
        self._taskLock = multiprocessing.Lock()
        self._retLock  = multiprocessing.Lock()
        self._workerLock  = multiprocessing.Lock()
        self._event    = multiprocessing.Event()

    def SubmitTask( self, tid, task, callback, *params ):

        newTask = Task()
        newTask.tid = tid
        newTask.task = task
        newTask.process = callback
        newTask.params = tuple(params)
        newTask.ret = None

        # print( self._taskLock )
        # print( self._taskQueue )
        # print( newTask )
        ThreadSafe.SafePush( self._taskLock, self._taskQueue, newTask )
        # print( self._taskQueue.qsize() )
        self._event.set()


    @staticmethod
    def AddAttr( inst, name, method ):
        cls = type(inst)
        if not hasattr( cls, '__perinstance' ):
            cls = type( cls.__name__, (cls, ), {} )
            cls.__perinstance = True
        setattr( cls, name, property( method ) )


class ProcessTaskMng( MultiTaskBase ):
    def __init__( self, num ):
        super( ProcessTaskMng, self ).__init__()
        self.CreateTaskQueue()
        self.__proc_num = num;

    def OnLazyInit( self ):
        # self.__workers = []
        # print( self.__class__ )
        # print( self.__class__.mro() )
        # for name in self.__dict__.keys():
        #     print( name )
        # print( '=' * 50 )
        # for name in dir(self):
        #     print( name )
        # print( getattr( self, '_ProcessTaskMng__workers' ) )
        # sys.exit(0)
        try :
            getattr( self, '_ProcessTaskMng__workers' )
        except AttributeError as e :
            self.CreateWorks( self.__proc_num )

    def CreateWorks( self, num ):
        event    = self._event
        lockTask = self._taskLock
        lockRet  = self._retLock
        lockWorker = self._workerLock
        taskQueue = self._taskQueue 
        retQueue  = self._retQueue
        workerDict = self._workerDict

        ''' 创建工作线程 '''
        self.__workers = []
        for procIdx in range( num ) :
            args = ( procIdx, event, lockTask, taskQueue, lockRet, retQueue, lockWorker, workerDict )
            # proc = multiprocessing.Process( target=ProcessTaskWorker.MakeInstance, args=args )
            proc = multiprocessing.Process( target=TaskWorkEntry, args=args )
            self.__workers.append( proc )
            proc.start()

    def SubmitTask( self, tid, task, callback, *params ):
        super( ProcessTaskMng, self ).SubmitTask( tid, task, callback, *params )
        self.OnLazyInit()

    def Join( self ):
        try:
            finish = False
            while not finish:
                finish = True
                if self._taskQueue.empty():
                    for id in self._workerDict.keys():
                        ThreadSafe.SafeSetValue( self._workerLock, self._workerDict, id, True )

                for proc in self.__workers:
                    proc.join(0.001)
                    if proc.is_alive():
                        finish = False
                        break
        except KeyboardInterrupt as e:
            # 准备正常结束
            finish = True
            self.SafeStopAllWork()
        except AttributeError as e:
            pass

    def SafeStopAllWork(self):
        # 通知所有的Worker停工
        self._taskLock.acquire()
        if self._taskQueue.empty():
            for id in self._workerDict.keys():
                ThreadSafe.SafeSetValue( self._workerLock, self._workerDict, id, True )
        self._taskLock.release()

class ThreadTaskMng( MultiTaskBase ):
    pass






class ProcessTaskWorker:

    def __init__( self, workerId, event, lockTask, taskQueue, lockRet, retQueue, lockWorker, workerDict ):
        self.__id       = workerId
        self.__event    = event
        self.__lockTask = lockTask
        self.__lockRet  = lockRet
        self.__lockWorker = lockWorker
        self.__taskQueue = taskQueue
        self.__retQueue = retQueue
        self.__workerDict = workerDict
        self.__stop     = False

        ProcessTaskWorker.__InitLog( workerId )

        # workerDict.put( self )
        ThreadSafe.SafeSetValue( lockWorker, workerDict, workerId, False )
        # ThreadSafe.SafePush( lockWorker, workerDict, workerId )

    @staticmethod
    def __InitLog( pid ):
        logmng.g_log = logmng.LogMng()
        logmng.g_log.initlog( Config.LogFile + str(pid) )

    def Run( self ):
        try:
            # self.__stop = False
            stop = ThreadSafe.SafeGetValue( self.__lockWorker, self.__workerDict, self.__id )
            while not stop:
                if self.__event.wait(0.5) and self.__event.is_set():
                    # print( self.__event.is_set() )
                    self.ProcQueue()
                else:
                    stop = ThreadSafe.SafeGetValue( self.__lockWorker, self.__workerDict, self.__id )
                    # print( self.__id, stop )
                # time.sleep(1)
        except KeyboardInterrupt as e:
            print( 'Worker %d Quit.' % (self.__id) )
            pass

    # @TimeKeep
    def ProcQueue( self ):
        # while not self.__stop:
        task = self.__GetTask()
        # if task is not None and task.process is not None:
        if task != None and task.process != None:
            # print( self.__id, ' ', end='')
            task.process( task.task, *task.params )


    # @TimeKeep
    def __GetTask( self ):
        def pop():
            task = None
            # print( self.__taskQueue.qsize() )
            if self.__taskQueue.qsize() > 0:
                task = self.__taskQueue.get_nowait()
            else:
                self.__event.clear()
            return task

        return self.__ThreadSafe( self.__lockTask, pop )

    def __ThreadSafe(self, locker, func):
        locker.acquire()
        if func is not None:
            ret = func()
        locker.release()
        return ret

    @staticmethod
    def MakeInstance( *args ):
        print( ProcessTaskWorker.MakeInstance.__name__ )

def TaskWorkEntry( *args ):
    # for arg in args :
    #     print( arg )
    worker = ProcessTaskWorker( *args )
    worker.Run()
    # print( 'TEST' )

# class AdvTaskMng() :
#     def __init__( self, nProc, nThread ):
#         """
#         nProc   : 生成几个工作进程
#         nThread : 每个进程启动几个工作线程
#         """
#         self.__worker = WorkerThread()

def TestTask( text, *args ):
    print( text, flush=True )

if __name__ == '__main__':
    mng = ProcessTaskMng(3)
    mng.SubmitTask( 0, 'test task', TestTask, None )
    while True:
        mng.SubmitTask( 0, 'test task', TestTask, None )
        # time.sleep(0.1)
    # ProcessTaskMng.MakeInstance()
    # print( mng )


