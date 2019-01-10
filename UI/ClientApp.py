# -*- coding:utf-8 -*-

import matplotlib
# 这个需要早一些执行
matplotlib.use('WXAgg')
import wx
from ClientFrame import Frame
from config import g_version

class App( wx.App ) :
    """UI 应用程序主体"""
    def __init__( self, redirect=True, filename=None ):
        ''' redirect : 是否使用输出窗口， 输出文件 '''
        wx.App.__init__( self, redirect, filename )
        self.Bind(wx.EVT_IDLE, self.OnIdle)

    def OnInit(self):
        self.__frame = Frame(
                parent = None,
                id = -1,
                title = u'MicroChat' + u' ' * 5 + u'Ver. %2d.%2d.%2d.%2d' % g_version )
        self.__frame.Show()
        self.SetTopWindow( self.__frame )

        return True

    def OnExit( self ):
        return 0
        # pass

    def OnIdle( self, evt ):
        # print( evt )
        # 得有事件后才会再收到这个事件
        pass

