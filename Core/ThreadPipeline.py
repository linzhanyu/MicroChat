from logmng import *
# from config import Config
# 至关重要的一句话居然没有就各种报错
# from DataSource.Common import *
from AdvTask import ThreadSafe, Task, MultiTaskBase, opList

import threading
# , time, os, sys, shutil, logging, copy, re
# 原子双向队列
from collections import deque
import unittest

'''
任务
多线程工作者
多线程管理器
多线程流水线
'''

# ------------------------------------------------------------
# 线程任务流水线
# ------------------------------------------------------------
class ThreadTaskPipeline( MultiTaskBase ):
    def __init__( self ):
        super( ThreadTaskPipeline, self ).__init__()

    def Init( self, worker_nums=() ):
        self._CreateTaskQueue( worker_nums )

    def Fini( self ):
        self.SafeStopAllWork()
        self.Join()

    def _CreateTaskQueue( self, worker_nums=() ):
        '''创建流水线层'''
        self._taskLock = threading.Lock()
        self.__stations = []
        self.__phase = len( worker_nums )
        for nums in worker_nums:
            # 事件, 任务队列锁, 任务队列, 线程ID队列
            station = (threading.Event(), threading.Lock(), deque(), {}, )
            evt, lock, taskQueue, tdic = station
            self.__stations.append( station )
            print( 'Create worker : ', nums )
            for i in range( nums ):
                worker = TaskThread( station, self )
                worker.start()
                tid = worker.ident
                tdic[ tid ] = worker

    def SubmitTask( self, task ):
        '''
        添加任务
        Params:
            task 任务
        '''

        if task.phase < self.__phase:
            evt, lock, tasks, tids = self.__stations[task.phase]
            ThreadSafe.SafeAccess( lock, lambda : opList( tasks, task ) )
            evt.set()
        else:
            LOG_ERROR('任务超出流水线')

    def Join( self ):
        try:
            finish = False
            while not finish:
                finish = True
                for pipeline in self.__stations:
                    evt, lock, tasks, tdic = pipeline
                    for tid, worker in tdic.items():
                        worker.join( 0.001 )
                        if worker.is_alive():
                            finish = False
                            break
                    if not finish :
                        break
        except KeyboardInterrupt :
            finish = True
            self.SafeStopAllWork()
        except Exception:
            print( traceback.format_exc(), file=sys.stderr )

    def SafeStopAllWork( self ):
        def StopAllWork( stations ):
            # print( 'Stop All' )
            for station in stations:
                evt, lock, tasks, tdic = station
                for tid, worker in tdic.items():
                    worker.stop()
        ThreadSafe.SafeAccess( self._taskLock, lambda : StopAllWork( self.__stations ) )

# ------------------------------------------------------------
# 任务处理线程
# ------------------------------------------------------------
class TaskThread( threading.Thread ):
    def __init__( self, station, pipeline ):
        super( TaskThread, self ).__init__()
        # threading.Thread.__init__( self )
        evt, lock, taskQueue, tdic = station
        self.__event  = evt
        self.__locker = lock
        self.__taskQueue = taskQueue
        self.__pipeline = pipeline
        self.__valid = True

    def run( self ):
        while( self.__valid ):
            if self.__event.wait(1):
                task = self.__GetTask()
                if task is None:
                    continue
                self.ProcTask( task )
        # print( '0x%08X : %s' % (threading.get_ident(), 'Thread Quit.') )

    def ProcTask( self, task ):
        if task.process is not None:
            task.process( self.__pipeline, *task.params )

    def stop( self ):
        self.__valid = False

    def __GetTask( self ):
        def pop():
            task = None
            if len(self.__taskQueue) > 0:
                task = self.__taskQueue.popleft()
            else:
                self.__event.clear()
            return task

        return ThreadSafe.SafeAccess( self.__locker, pop )

# ------------------------------------------------------------
# UnitTest
# ------------------------------------------------------------

class testTaskPipeline( unittest.TestCase ):
    @classmethod
    def setUpClass( self ):
        self.pipeline = ThreadTaskPipeline()
        self.pipeline.Init( ( 1, 2 ) )

    @classmethod
    def tearDownClass( self ):
        self.pipeline.Fini()

    def testAddTask1( self ):
        def ProcFunc( pipeline, msg ):
            print( '0x%08X : %s' % (threading.get_ident(), msg) )
        task = Task()
        task.phase = 0
        task.process = ProcFunc
        task.params = tuple( ('I am is a message.', ) )
        self.pipeline.SubmitTask( task )
        time.sleep( 0.02 )

    def testAddTask2( self ):
        def ProcFunc0( pipeline, msg ):
            print( '0x%08X : %s' % (threading.get_ident(), msg) )

        def ProcFunc1( pipeline, msg ):
            ProcFunc0( self.pipeline, msg )
            task = Task()
            task.phase = 1
            task.process = ProcFunc0
            task.params = tuple( ('处理结果 1.', ) )
            self.pipeline.SubmitTask( task )
        task = Task()
        task.phase = 0
        task.process = ProcFunc1
        task.params = tuple( ('处理任务 0.', ) )
        self.pipeline.SubmitTask( task )
        time.sleep( 0.02 )


def suite():
    suite = unittest.TestSuite()
    suite.addTest( testTaskPipeline('testAddTask1' ) )
    suite.addTest( testTaskPipeline('testAddTask2' ) )
    return suite

