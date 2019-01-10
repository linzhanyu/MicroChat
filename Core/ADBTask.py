# -*- coding:utf-8 -*-
import time, os
from config import Config

############################################################
# 注： 这一部分的任务和 Task 系列的没有关系。
############################################################

class CommonTask :
    def __init__( self ):
        cmd = os.path.join(Config.ADK, 'platform-tools', 'adb.exe')
        self.adb = os.path.join(cmd, 'platform-tools', 'adb.exe')
        # print( self.adb )
        self.__finish = False

    def Execute( self ):
        '''执行'''
        pass

    def isFinish( self ):
        '''是否结束'''
        return self.__finish

# 命令行任务
class CmdTask( CommonTask ):
    def __init__( self, process, parse=None ):
        CommonTask.__init__(self)
        self.__process = process
        self.__parse   = parse

    def Execute( self ):
        # print('Run . ')
        self.__process.run()
        self.__parse( self.__process.stdout )
        self.__finish = True

# 循环处理的任务
class LoopTask( CommonTask ):
    def __init__( self, task, interval, count=-1 ):
        CommonTask.__init__( self )
        self.task = task
        self.interval = interval
        self.count = -1
        self.lastRun = 0.0

    def Execute( self ):
        if not self.task :
            self.__finish = True
            return

        curTime = time.time()
        if curTime - self.lastRun < self.interval:
            return

        self.task.Execute()
        self.lastRun = curTime

        if self.count > 0:
            self.count -= 1
        elif self.count == 0:
            self.__finish = True
        else:
            pass


