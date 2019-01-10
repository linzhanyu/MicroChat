# -*- coding:utf-8 -*-
import sys
# if sys.version_info.major == 2:
#     import thread
# elif sys.version_info.major == 3:
#     import _thread as thread
import threading, time, os, sys, shutil, logging, copy, re
# 原子双向队列
from collections import deque
from ThreadPipeline import ThreadTaskPipeline
import unittest

# if sys.version_info.major == 3 :
#     from queue import Queue
# else:
#     from Queue import Queue

# import wx
# from CustomEvent import *
# from config import g_config, eStorage
# from File import *

# ============================================================
# 任务处理线程
class TaskThread( threading.Thread ):
    def __init__(self):
        threading.Thread.__init__( self )
        self.tasks = []
        # self.lock = threading.Lock()
        self.task_locker = threading.Lock()
        self.running = True

    def AddTask( self, task ):
        self.task_locker.acquire()
        logging.info( 'Add Task.' )
        self.tasks.append( task )
        # logging.info( '====> %s' % ( str(task.config) ) )
        self.task_locker.release()

    def PostEvent( self, task, bLock ):
        wnd = task.config['window']
        evt = clientEVT_TASK_FINISH( data=bLock )
        wx.PostEvent( wnd, evt )
        # print( '.' * 10 )
        wnd.GetEventHandler().QueueEvent( evt.Clone() )

    def run( self ):
        task = None
        while self.running:
            self.task_locker.acquire()
            if len( self.tasks ) :
                task = self.tasks.pop(0)
            else:
                task = None
            self.task_locker.release()

            if task == None:
                time.sleep( 0.1 )
                continue
            else:
                # print( u'执行任务.' )
                self.PostEvent( task, True )
                # logging.info( '=====> %s' % ( str(task.config) ) )
                try:
                    bRet = task.Execute()
                except RuntimeError as e:
                    logging.critical( u'发现异常 执行 %s' % (u'失败',) )
                    # raise e
                else:
                    logging.critical( u'任务执行 %s' % (bRet and u'成功' or u'失败',) )

                self.PostEvent( task, False )

                # self.task_locker.acquire()
                # if len( self.tasks ) > 0:
                #     self.tasks.remove(0)
                #     # del self.tasks[0]
                # # print( len(self.tasks) )
                # self.task_locker.release()

    def stop( self ):
        self.running = False

class TaskThreadBase( threading.Thread ):
    def __init__( self ):
        threading.Thread.__init__( self )
        self.__locker = threading.Lock()
        self.__event = threading.Event()
        self.__event.clear()
        self.__taskQueue = deque()
        self.__valid = True

    # 因为是多线程.不能直接用 callback
    def SubmitTask( self, tid, callback, task, *params ):
        def push():
            # print(type(task))
            # print(type(params), params)
            self.__taskQueue.append( (tid, callback, task, params) )
            # self.__taskQueue.put( task )
            self.__event.set()

        self.__ThreadSafe( push )

    def run( self ):
        print( '%s thread id : 0x%X'% (self.__class__.__name__, self.ident,) )
        while( self.__valid ):
            if self.__event.wait(1):
                task = self.__GetTask()
                if task is None:
                    continue
                id, cbs, func, params = task
                ret = None
                if func is not None:
                    # print( id, cbs, func )
                    ret = func( *params )
                if cbs is not None:
                    cb, cb0 = cbs
                    if cb != None:
                        cb(id, cb0, ret)

    def stop( self ):
        self.__valid = False
        self.__taskQueue.clear()

    def __ThreadSafe(self, func):
        self.__locker.acquire()
        if func is not None:
            ret = func()
        self.__locker.release()
        return ret

    def __GetTask( self ):
        def pop():
            task = None
            if len(self.__taskQueue) > 0:
                task = self.__taskQueue.popleft()
            else:
                self.__event.clear()
            return task

        return self.__ThreadSafe( pop )

# 任务处理工作线程
class WorkerThread( TaskThreadBase ):
    def __init__(self):
        TaskThreadBase.__init__(self)

# 结果处理工作线程
class CDNThread( TaskThreadBase ):
    def __init__(self):
        TaskThreadBase.__init__(self)

# 2018-02-24 使用 pipline 代替原有的线程处理方式
class TaskMng():
    def __init__(self):
        # self.__worker = WorkerThread()
        # self.__worker.start()
        # self.__cdn = CDNThread()
        # self.__cdn.start()

        self.__pipeline = ThreadTaskPipeline()
        self.__pipeline.Init( (5, ) )

    # 因为是多线程.不能直接用 callback
    # 其实设计的应该是一个流水线
    # 中转 callback 机制似乎可以实现流水线
    # def SubmitTask( self, tid, callback, task, *params ):
    #     self.__worker.SubmitTask( tid, (self.__TCBRet, callback), task, *params )
    def SubmitTask( self, *args, **kw ):
        self.__pipeline.SubmitTask( *args, **kw )

    def Destroy( self ):
        # self.__worker.stop()
        # self.__cdn.stop()
        self.__pipeline.Fini()

    def Join( self ):
        # self.__worker.join()
        # self.__cdn.join()
        self.__pipeline.Join()

    # # Thread callback function
    # def __TCBRet( self, id, func, ret ):
    #     # self.__cdn.SubmitTask( self.
    #     # print( id, ret )
    #     self.__cdn.SubmitTask( id, None, func, ret )

    # def __ProcRetLoop( self ):
    #     pass

# ------------------------------------------------------------
# UnitTest
# ------------------------------------------------------------
class testTaskMng( unittest.TestCase ):
    @classmethod
    def setUpClass(self):
        self.mng = TaskMng()

    @classmethod
    def tearDownClass(self):
        self.mng.Destroy()

    def testAddTask(self):
        self.tid = threading.get_ident()
        # print( self.tid )
        def threadTask( id ):
            tid = threading.get_ident()
            print( '%5d : 0x%08X 0x%08X' % (id, tid, self.tid) )

        for i in range(10):
            # print( 'Add Task %5d : 0x%08X' % (i, thread.get_ident() ) )
            self.mng.SubmitTask( threadTask, None, None, i )
        time.sleep(0.02)

    def testAddTask2(self):
        self.tid = threading.get_ident()
        def threadTask():
            tid = threading.get_ident()
        self.mng.SubmitTask( threadTask, None, None, self.tid )

    def testAddWorkerThread(self):
        print('')
        worker = WorkerThread()
        worker.start()
        time.sleep(0.1)
        worker.stop()
        worker.join()

    def testAddCDNThread(self):
        print('')
        worker = CDNThread()
        worker.start()
        time.sleep(0.1)
        worker.stop()
        worker.join()

def suite():
    suite = unittest.TestSuite()
    suite.addTest( testTaskMng('testAddTask') )
    suite.addTest( testTaskMng('testAddTask2') )
    suite.addTest( testTaskMng('testAddWorkerThread') )
    suite.addTest( testTaskMng('testAddCDNThread') )
    return suite

# # ============================================================
# # 单任务
# class Task :
#     def __init__( self ):
#         pass
# 
#     def __init__( self, taskConfig ):
#         self.config = taskConfig
# 
#     # 取平台名字
#     def PlatformName( self ):
#         packages = []
#         os_name = self.config['OS']
#         platform_name = ''
#         # print( self.config['Platform']['Optional'] )
#         for item in self.config['Platform']['Optional']:
#             platform_name = item[0]
#         return platform_name
# 
#     # 取 AutoBuilder 所在的目录
#     def GetAutoBuilderDir( self ):
#         return os.path.dirname(g_config['AutoBuilderPath'])
# 
#     # 取得 AutoBuilder 使用的配置文件的目录
#     def GetConfDir( self ):
#         conf_path = os.path.join( self.GetAutoBuilderDir(), g_config['MiniClientConfig'] )
#         return conf_path
# 
#     def GetTemplateDir(self):
#         return 'template'
# 
#     # 将配置中的系统名转换成转换成Plugin中的相应目录名
#     def TranslateDirName( self, os_name ):
#         if os_name == 'IOS':
#             return 'iOS'
#         return os_name
# 
#     # 将配置中的系统名转换成Unity编译时用的Target名字
#     # same Unity.BuildTarget.xxx
#     def TranslateBuildTargetName( self, os_name ):
#         build_target = os_name
#         if os_name == 'IOS':
#             build_target = 'iPhone'
#         return build_target
# 
# 
#     # same Unity.RuntimePlatform.xxx
#     def TranslateRuntimePlatformName( self, os_name ):
#         if os_name == 'IOS':
#             return 'IPhonePlayer'
#         return os_name
# 
#     def GetTargetName( self ):
#         os_name = self.config['OS']
#         return self.TranslateBuildTargetName( os_name )
# 
#     def GetTargetDir( self ):
#         # return self.GetTargetName()
#         os_name = self.config['OS']
#         return self.TranslateDirName( os_name )
# 
#     def GetProjectTargetDir( self ):
#         return self.TranslateBuildTargetName( self.config['OS'] )
# 
#     def GetRuntimePlatformName( self ):
#         return self.TranslateRuntimePlatformName( self.config['OS'] )
# 
#     # 取得 Platform 所在的目录
#     def GetPlatformDir( self ):
#         os_name = self.config['OS']
#         platform_root = os.path.join( self.GetProjectDir(), 'platform' )
#         platform_dir = os.path.join( platform_root, self.TranslateDirName(os_name) )
#         return platform_dir
# 
#     # 取得 san-programer 的目录
#     def GetProjectDir( self ):
#         raise
# 
#     def GetPublishDir( self ):
#         return g_config['release_dir']
# 
#     # 复制文件
#     def CopyFile( self, src, dst ):
#         shutil.copyfile( src, dst )
# 
#     def StepTip( self, msg ):
#         logging.info( u'='*50 + u' ' + msg )
# 
#     def RmDir( self, local_dir ):
#         while True:
#             try:
#                 if os.path.exists( local_dir ):
#                     logging.info( u'删除目录 : %s' % (local_dir, ) )
#                     shutil.rmtree( local_dir )
#                 break
#             except OSError as e:
#                 logging.warning( u'无法删除 : %s' % (local_dir, ) )
#                 time.sleep(1.0)
#         return not os.path.exists( local_dir )
# 
#     def Du( self, local_dir ):
#         size = 0
#         for root, dirs, files in os.walk(local_dir):
#             size += sum([os.path.getsize(os.path.join(root, name)) for name in files] )
#         return size
# 
#     # def Execute( self ):
#     #     logging.debug( u'%s %s'% (str(self), u'TEST...') )
#     #     return False
# 
# # ============================================================
# # 任务队列
# class TaskQueue( Task ):
#     def __init__( self ):
#         Task.__init__( self )
#         self.__queue = []
# 
#     def Append( self, task ):
#         self.__queue.append( task )
# 
#     def Execute( self ):
#         bRet = True
#         for task in self.__queue:
#             bRet = task.Execute()
#             if not bRet:
#                 break
#         return bRet
# 
# # ============================================================
# # Mini Client 相关任务
# class TaskMiniClient( Task ):
#     def __init__( self, taskConfig ):
#         Task.__init__( self, taskConfig )
# 
#     def GetClientName( self ):
#         return 'MiniClient'
#         # if 'Clinet' in self.config.keys() and self.config['Client'] == 'MiniClient':
#         #     return 'MiniClient'
#         # else:
#         #     return 'client'
# 
#     # 取得 san-programer 的目录
#     def GetProjectDir( self ):
#         return os.path.abspath(g_config['project_dir'])
# 
#     def GetClientDir( self ):
#         return os.path.join( self.GetProjectDir(), self.GetClientName() )
# 
#     def GetAssetsDir( self ):
#         return os.path.join( self.GetClientDir(), 'Assets' )
# 
#     def GetIconDir( self ):
#         return os.path.join( self.GetAssetsDir(), 'Icon' )
# 
#     def GetClientReleaseDir( self ):
#         return os.path.join( self.GetClientDir(), 'Release', self.GetTargetName() )
# 
#     def GetAppFileName( self ):
#         filename = ''
#         if self.GetTargetName() == 'iPhone' :
#             filename = 'SanGuoXIOS.ipa'
#         else:
#             filename = 'SanGuoX.apk'
#         return filename
# 
# # ============================================================
# # Client 相关任务
# class TaskClient( TaskMiniClient ):
#     def __init__( self, taskConfig ):
#         TaskMiniClient.__init__(self, taskConfig)
# 
#     def GetProjectDir( self ):
#         if 'Branch' in self.config.keys():
#             if self.config['Branch'] == '__localhost__':
#                 return TaskMiniClient.GetProjectDir(self)
#         return os.path.abspath(g_config['client_root_dir'])
# 
#     def GetClientName( self ):
#         return 'client'
# 
#     def GetClientReleaseAssetDir( self ):
#         return os.path.join( self.GetClientReleaseDir(), 'Asset' )
# 
#     def GetProjectReleaseDir( self ):
#         return os.path.join( self.GetProjectDir(), 'Release' )
# 
#     def GetProjectReleaseWorkDir( self ):
#         return os.path.join( self.GetProjectReleaseDir(), g_config['MiniClientConfig'] )
# 
#     def GetProjectReleaseTargetDir( self ):
#         return os.path.join( self.GetProjectReleaseWorkDir(), self.GetProjectTargetDir() )
#         # return os.path.join( self.GetProjectReleaseDir(), g_config['MiniClientConfig'], self.GetTargetName() )
# 
#     def GetProjectReleaseAssetDir( self ):
#         return os.path.join( self.GetProjectReleaseTargetDir(), 'Asset' )
# 
#     def GetProjectReleaseConfDir( self ):
#         return os.path.join( self.GetProjectReleaseWorkDir(), 'tagRoot' )
# 
#     def GetCodeTagName( self ):
#         return self.config['Tag']
# 
#     # svn tag name
#     def GetReleaseTagName( self ):
#         return 'cloud_%s' % ( self.GetCodeTagName(), )
# 
#     # svn tag dir
#     def GetReleaseTagDir( self ):
#         return '/tags/%s' % (self.GetReleaseTagName(), )
# 
#     # svn tag assets dir
#     def GetReleaseTagAssetDir( self ):
#         return '%s/ResourceAssets/%s/Asset/' % ( self.GetReleaseTagDir(), self.GetRuntimePlatformName() )
# 
#     def FixVerControlDir( self, enum_type, remote_path, local_dir ):
#         from Core import core
#         if enum_type == eStorage.PROGRAMMER:
#             vc = core.code
#         elif enum_type == eStorage.RELEASE:
#             vc = core.release
# 
#         if os.path.exists( local_dir ):
#             returncode = vc.CleanupDir( local_dir, logging.debug )
#             if returncode != 0 : return False
#             returncode = vc.SwitchDir( remote_path, local_dir, logging.debug )
#             if returncode != 0 : return False
#             # returncode = vc.RevertDir( '.', [local_dir, ], logging.debug )
#             # if returncode != 0 : return False
#         else:
#             os.makedirs( local_dir )
#             returncode = vc.CloneDir( remote_path, local_dir, cb_line_proc=logging.debug )
# 
#         if returncode == 0:
#             returncode = vc.UpdateDir( local_dir, logging.debug )
# 
#         return returncode == 0
# 
#     def GetClientVersion( self ):
#         local_path = os.path.join( self.GetAssetsDir(), 'Scene', 'intro', 'client_setting.txt' )
#         c = load_file( local_path )
#         m = re.search( r'(\d+)\.(\d+).(\d+)', c)
#         if m is not None:
#             return m.group(0)
#         return None
# 
#         
# 
# # ============================================================

