# -*- coding:utf-8 -*-

from __future__ import print_function
import subprocess, os, sys

class SubProcess():
    def __init__( self, cmd, run_dir, line_proc=None, shell=True ):
        self.cmd = cmd
        self.run_dir = run_dir
        self.out_func = line_proc
        self.shell = shell
        self.__p = None
        self.stdout = None

    def run( self ):
        newEnv = os.environ.copy()
        newEnv['LC_MESSAGES'] = 'en'

        info = subprocess.STARTUPINFO()
        info.wShowWindow = False
        info.dwFlags=subprocess.SW_HIDE
        if os.name == 'nt':
            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        try:
            self.__p = subprocess.Popen(
                    self.cmd,
                    env=newEnv,
                    cwd=self.run_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    startupinfo=info,
                    shell=self.shell)
            self.stdout = self.__p.stdout
            # print( self.__p, self.stdout )
        except OSError as e:
            # f = sys.stderr
            # print( 'Execute %s failed.' % (self.cmd[0], ), '', '\n', f )
            # print( 'Execute %s failed.' % (self.cmd[0], ), file=sys.stderr )
            raise e

    def kill(self):
        if self.__p != None:
            self.__p.kill()
            self.__p = None
            self.stdout = None

    def __del__(self):
        self.kill()







