# -*- coding:utf-8 -*-
import wx
import wx.richtext as rt
import os, platform, string, sys
if sys.version_info.major == 2:
    import wx.aui as aui
elif sys.version_info.major == 3:
    import wx.lib.agw.aui as aui

# from ConfigurePanel import ConfigurePanel
from DebugPanel import DebugPanel
from CustomEvent import *
from MicroChatPanel import MicroChatPanel
from wxLogHandler import *
from Core.Core import core
from AdvTask import Task
from logmng import g_log
from Log import DebugLog
from config import Config

ALLOW_AUI_FLOATING = False
XRCFILE = 'xrc/Frame.xrc'

LOG = sys.version_info.major == 2 and wx.PyLog or wx.Log

class MyLog( LOG ):
    def __init__( self, textCtrl, logTime=0 ):
        LOG.__init__(self)
        self.tc = textCtrl
        self.logTime = logTime

    def DoLogString( self, message, timeStamp ):
        msg = message.lower()
        err_keys = ['stderr', 'failed', 'error', 'exception', ]
        warning_keys = ['warning', ]
        find_key = False
        if 'SetFocus' in msg :
            return

        for key in err_keys:
            if key in msg:
                find_key = True
                break
        if find_key:
            self.tc.SetDefaultStyle( wx.TextAttr(wx.YELLOW, wx.RED) )
        else:
            for key in warning_keys:
                if key in msg:
                    find_key = True
                    break
            if find_key:
                self.tc.SetDefaultStyle( wx.TextAttr(wx.WHITE, wx.BLUE) )
            else:
                self.tc.SetDefaultStyle( wx.TextAttr(wx.BLACK, wx.LIGHT_GREY) )
        if self.tc:
            self.tc.AppendText( message+'\n' )

class Frame( wx.Frame ):

    mainFrame = None

    def __init__( self, parent, id, title ):
        wx.Frame.__init__( self, parent, id, title, \
                pos = wx.DefaultPosition,\
                size = (1024,768),\
                style = wx.DEFAULT_FRAME_STYLE,\
                name = 'frame' )
        Frame.mainFrame = self
        self.__InitXRC()
        self.SetMinSize( (800, 600) )

        self.haveFocus = False

        # pnl = wx.Panel(self)
        # self.pnl = pnl
        self.mgr = aui.AuiManager()
        self.mgr.SetManagedWindow( self )

        icon = wx.Icon( name = 'res/Python.ico', type = wx.BITMAP_TYPE_ICO )
        self.SetIcon( icon )

        if sys.version_info.major == 2:
            self.statusBar = self.CreateStatusBar(2, wx.ST_SIZEGRIP)
        elif sys.version_info.major == 3:
            self.statusBar = self.CreateStatusBar(2, wx.STB_SIZEGRIP)
        self.statusBar.SetStatusWidths([-2, -1])

        statusText = u'MicroChat use wxPython %s'%wx.version()
        self.statusBar.SetStatusText(statusText, 0)

        if platform.system() == 'Windows' :
            ctrl_style = wx.TE_RICH|wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL|wx.NO_BORDER
        else:
            ctrl_style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL|wx.NO_BORDER

        # self.log = rt.RichTextCtrl( self, style=wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER|rt.RE_READONLY )
        self.log = wx.TextCtrl(self, wx.ID_ANY, style = ctrl_style )
        if sys.version_info.major == 2:
            wx.Log_SetActiveTarget(MyLog(self.log))
        elif sys.version_info.major == 3:
            wx.Log.SetActiveTarget(MyLog(self.log))

        # self.mgr.AddPane( ConfigurePanel(self, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN, log=self.log),
        #         aui.AuiPaneInfo().
        #         Centre().Layer(2).BestSize((240,-1)).
        #         MinSize((160,-1)).
        #         Floatable(ALLOW_AUI_FLOATING).FloatingSize((240,700)).
        #         Caption(u'Configure').
        #         CloseButton(False).
        #         Name(u'A2'))

        s = aui.AUI_NB_SCROLL_BUTTONS | aui.AUI_NB_TAB_EXTERNAL_MOVE | aui.AUI_NB_TAB_FIXED_WIDTH | aui.AUI_NB_TAB_SPLIT | aui.AUI_NB_TOP | aui.AUI_NB_WINDOWLIST_BUTTON
        # | aui.AUI_NB_LEFT
        # | aui.AUI_NB_RIGHT
        # | aui.AUI_NB_TAB_MOVE
        # | aui.AUI_NB_BOTTOM
        self.nb = aui.AuiNotebook(self, style=s)


        page = MicroChatPanel(self, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN, log=self.log)
        stockPanel = page
        # DataMngr().ob_ui.panels.append( page )
        # page.draw()
        self.nb.AddPage( page, u'MicroChat' )
        
        self.mgr.AddPane( self.nb,
                aui.AuiPaneInfo().
                Centre().Layer(2).BestSize((240,-1)).
                MinSize((160,-1)).
                Floatable(ALLOW_AUI_FLOATING).FloatingSize((240,700)).
                Caption(u'Configure').
                CloseButton(False).
                MaximizeButton(True).
                Name(u'A2'))

        self.mgr.AddPane(self.log, aui.AuiPaneInfo().
                Caption(u'Log Messages').
                Right().Layer(1).Position(1).BestSize((-1,80)).
                Dockable(False).
                MinSize((-1,80)).
                Floatable(ALLOW_AUI_FLOATING).FloatingSize((500,160)).
                CloseButton(True).
                MaximizeButton(True).
                Name(u'A3'))
        self.mgr.Update()
        if sys.version_info.major == 2:
            self.mgr.SetFlags(self.mgr.GetFlags() ^ aui.AUI_MGR_TRANSPARENT_DRAG)

        # 绑定事件处理
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.Bind(EVT_TASK_FINISH, self.OnTaskFinish )
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGING, self.OnPageChangeine )

        self.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)
        # self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)

        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.Bind(wx.EVT_CHAR, self.OnChar)
        self.Bind(wx.EVT_MOVE, self.OnMove)

        # LOG
        self.Bind( EVT_WX_LOG_EVENT, self.OnLogEvent )
        self.uilog = wxLogHandler(self)
        if g_log is not None:
            g_log.AddHandler( self.uilog )

        self.SetFocus()

        # self.searchDlg = wx.Dialog(self, -1, 'test dlg')
        self.nb.SetSelection(0)
        # self.nb.ChangeSelection(1)

        # wx.LogError('test log error')
        # wx.LogWarning('test log warning')
        # wx.LogDebug('test log debug')
        # stockPanel.LoadDataFromHDF5( 'sz002487' )
        # stockPanel.LoadDataFromHDF5( 'sh000001' )
        # stockPanel.LoadDataFromHDF5( 'sz000666' )
        # stockPanel.LoadDataFromHDF5( Config.stock, Config.kType )
        # stockPanel.LoadDataFromHDF5( 'sz300315' )

        # Start Work Thread
        def RunOtherThread( *args ):
            pass
            # print( 'RunOtherThread', *args )
            # start = -1
            # end = -1
            # pipeline, code, ktype, rtype = args
            # df = DataMngr.GetKBarDF( code, ktype, start, end, rtype=rtype )
            # if df is not None:
            #     wx.CallAfter( stockPanel.OnDFLoaded, df )

        # core.taskMng.SubmitTask( core.tid, None, RunOtherThread, 1 )
        # Test new thread task pipline.
        task = Task()
        task.phase = 0
        task.process = RunOtherThread
        # task.params = (Config.stock, Config.kType, Config.rtype)
        task.params = ()
        core.taskMng.SubmitTask( task )

        # TODO :
        # 1. 加载 Basics 基本面数据
        # 2. 启动数据增量更新线程（多）
        # 3. 数据增量模型分析线程（多）
        # 4. 

    def OnLogEvent( self, evt ):
        DebugLog( evt.message )
        evt.Skip()

    def OnCloseWindow(self, evt):
        # wx.Log_SetActiveTarget(None)
        if g_log is not None:
            g_log.RemoveHandler( self.uilog )
        self.Destroy()

    def OnTaskFinish( self, evt ):
        print( 'FInish.' + str(evt.GetInt()) )

    def OnPageChangeine( self, evt ):
        # print( 'Change page to ' + str(evt.GetSelection()) )
        pageId = evt.GetSelection()
        paneinfo = self.mgr.GetPane( self.log )
        if pageId == 0:
            # self.mgr.DetachPane( self.log )
            # self.log.Hide()
            # paneinfo.Hide()
            # paneinfo.Show(False)
            # paneinfo.MaxSize()
            # paneinfo.Show(True)
            paneinfo.Show(sys.version_info.major == 2)
        else:
            self.mgr.ClosePane( paneinfo )
            # self.mgr.
            # self.log.Show()
        self.mgr.Update()

    def OnSetFocus( self, evt ):
        pass
        # wx.LogDebug( 'Frame focus.' )
        # self.haveFocus = True
        # self.Refresh()

    # def OnKillFocus( self, evt ):
    #     self.haveFocus = False
    #     self.Refresh()

    def OnMouse( self, evt ):
        # wx.LogDebug( 'mouse evt : %s' % (evt,) )
        if evt.ButtonDown() :
            self.SetFocus()
        evt.Skip()

    def OnKeyDown( self, evt ):
        # wx.LogDebug('key down %d' % (evt.GetKeyCode(), ))
        evt.Skip()

    def OnKeyUp( self, evt ):
        # wx.LogDebug('key up %d' % (evt.GetKeyCode(), ))
        evt.Skip()

    def OnChar( self, evt ):
        # wx.LogDebug('char %d' % (evt.GetKeyCode(), ))
        try:
            s = chr(evt.GetKeyCode())
        except ValueError as e:
            evt.Skip()
            return

    def OnMove( self, evt ):
        # wx.LogDebug('Move %s' % (evt.GetPosition(), ))
        evt.Skip()

    def __GetSearchPos( self, size ):
        # baseWnd = self.nb.GetPage(0)
        # s = baseWnd.GetClientSize() - size
        # return wx.Point(s.GetWidth(), s.GetHeight())

        statusBarSize = self.statusBar.GetSize()
        border = self.GetSize() - self.GetClientSize()
        pos = self.GetSize() - size
        # print(border)
        pos.SetWidth( pos.GetWidth() - border.GetWidth() / 2 )
        pos.SetHeight( pos.GetHeight() - border.GetHeight() )
        pos = wx.Point(pos.GetWidth(), pos.GetHeight())
        # pos = wx.Point(pos.GetWidth(), pos.GetHeight())
        pos += self.GetPosition()
        return pos

    def __InitXRC( self ):
        resourceText = open( XRCFILE ).read()
        if sys.version_info.major == 2:
            wx.FileSystem_AddHandler( wx.MemoryFSHandler() )
            wx.MemoryFSHandler_AddFile( XRCFILE, resourceText )
        elif sys.version_info.major == 3:
            wx.FileSystem.AddHandler( wx.MemoryFSHandler() )
            # wx.MemoryFSHandler.AddFile( filename=XRCFILE, image=resourceText )
            wx.MemoryFSHandler.AddFileWithMimeType( XRCFILE, resourceText, 'xrc' )


