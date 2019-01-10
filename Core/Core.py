# -*- coding:utf-8 -*-

from singleton import Singleton
from Task import TaskThread, TaskMng
from EventMngr import EventMngr
import Task
import ThreadPipeline
from Observer import Subject, Observer
from config import *
# from dbi import *

import sys, copy, threading, time
import unittest

if sys.version_info.major == 2:
    import thread
elif sys.version_info.major == 3:
    import _thread as thread

class Core(Singleton) :
    def __init__(self):
        Singleton.__init__(self)
        # self.config = {}
        # self.task_thread = TaskThread()
        self.taskMng = TaskMng()
        self.eventMng = EventMngr()

        self.tid = thread.get_ident()
        # self.workers = 
        # 工作计算成员 池
        # 分配器、调度器
        # 注意它的执行线程
        self.subjectTask = Subject()
        self.__taskId = 0
        self.__valid = True
        self.__event = threading.Event()
        self.__retList = []

    def Init(self):
        # TODO : 检测一下网络连接状态
        # sql = 'SELECT basics.code AS code, name, d_last, 5_last FROM basics LEFT JOIN lasttime ON (basics.code = lasttime.code) group by code'
        # # 'select basics.code, name from basics left join lasttime on (basics.code = lasttime.code) group by code limit 10;'
        # self.SubmitTask(self.TestCallBack, DBI.SQLQuery, sql)
        self.eventMng.Init()
        self.eventMng.Start()
        return True

    def TestCallBack(self, *params):
        ret, = params
        ret = ret.set_index('code')
        print( 'TestCallBack' )
        print( ret )
        # print(ret[0])

    def Fini(self):
        self.taskMng.Destroy()
        self.taskMng.Join()
        self.eventMng.Stop()
        # self.task_thread.stop()
        # if self.task_thread.is_alive():
        #     self.task_thread.join()

    def MainLoop( self ):
        return
        # time.sleep(1.1)

        # TODO : move to TaskMng.ProcRetLoop
        # self.taskMng.ProcRetLoop()
        # while self.__valid :
        #     if self.__event.wait(1):
        #         while len(self.__retList) > 0:
        #             pass
        #     pass

    # def SubmitTask( self, callback, func, *params ):
    #     taskId = self.__alloc_task_id()
    #     self.taskMng.SubmitTask( taskId, callback, func, *params )
    #     # self.taskMng.SubmitTask( task[0], *(task[1:]) )

    def __alloc_task_id( self ):
        self.__taskId += 1
        return self.__taskId

    # def ReloadConfig(self):
    #     pass

    # def GetConfig( self ):
    #     return self.config

    # def SubmitTask( self, taskConfig ) :
    #     task_type = taskConfig['Type']
    #     target_name = taskConfig['Client']
    #     taskClass = None
    #     vCreateDef = [
    #             # ('Build',       'MiniClient',   TaskBuildMini ),
    #             # ('Build',       'Client',       TaskBuildClient ),
    #             # ('Build',       'AssetBundle',  TaskBuildBundle ),
    #             # ('Cleanup',     'MiniClient',   TaskVCMiniCleanup ),
    #             # ('Cleanup',     'Client',       TaskVCClientCleanup ),
    #             # ('Cleanup',     'AssetBundle',  TaskVCClientCleanup ),
    #             # ('Revert',      'MiniClient',   TaskVCMiniRevert ),
    #             # ('Revert',      'Client',       TaskVCClientRevert ),
    #             # ('Revert',      'AssetBundle',  TaskVCClientRevert ),
    #             # ('Remove',      'MiniClient',   None ),
    #             # ('Remove',      '*',            TaskClientRemove ),
    #             # ('APKInstall',  '*',            TaskAndroidInstall ),
    #             # ('APKUninstall','*',            TaskAndroidUninstall ),
    #             # ('APKStart',    '*',            TaskAndroidStart ),
    #             # ('APKStop',     '*',            TaskAndroidStop ),
    #             # ('Test',        '*',            TaskVCBundleUpdate ),
    #             ]
    #     found = False
    #     for task, target, Class in vCreateDef:
    #         if task == task_type:
    #             if target == target_name:
    #                 found = True
    #                 taskClass = Class
    #     if found == False:
    #         for task, target, Class in vCreateDef:
    #             if task == task_type:
    #                 if target == '*':
    #                     found = True
    #                     taskClass = Class

    #     if found == True:
    #         # print( taskClass )
    #         if taskClass != None :
    #             optionals = taskConfig['Platform']['Optional'][:]
    #             if len(optionals) > 0 and (target_name == 'Client' or target_name == 'MiniClient'):
    #                 # 将多个任务分解为单个任务
    #                 # logging.info( '===> %s' % ( str(optionals) ) )
    #                 for optional in optionals:
    #                     wnd = taskConfig['window']
    #                     taskConfig.pop('window')
    #                     # logging.info( '====> %s' % ( str(taskConfig) ) )
    #                     signalConf = copy.deepcopy( taskConfig )
    #                     signalConf['window'] = wnd
    #                     taskConfig['window'] = wnd
    #                     # signalConf = taskConfig
    #                     signalConf['Platform']['Optional'] = [optional, ]
    #                     task = taskClass( signalConf )
    #                     # logging.info( '===>> %s' % ( str(signalConf) ) )
    #                     
    #                     self.task_thread.AddTask( task )
    #             else:
    #                 task = taskClass( taskConfig )
    #                 self.task_thread.AddTask( task )

    #         if not self.task_thread.is_alive():
    #             self.task_thread.start()

core = Core()
__all__ = ['Core', 'core', 'suite',]

# ------------------------------------------------------------
# UnitTest
# ------------------------------------------------------------
class testCore( unittest.TestCase ):
    @classmethod
    def setUpClass(self):
        print( u'Create core Env.' )

    @classmethod
    def tearDownClass(self):
        print( u'Release core Env.' )

    def testCaseCore(self):
        pass

def suite():
    suite = unittest.TestSuite()
    suite.addTest( Calendar.suite() )
    suite.addTest( Task.suite() )
    suite.addTest( ThreadPipeline.suite() )
    suite.addTest( testCore('testCaseCore') )
    return suite

