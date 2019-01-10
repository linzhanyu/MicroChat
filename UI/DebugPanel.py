# -*- coding:utf-8 -*-
import wx
import wx.richtext as rt
from Core.Core import core
# from config import g_config, g_bundle_order
import os, sys

class DebugPanel( wx.Panel ):
    def __init__( self, parent, style, log ):
        wx.Panel.__init__( self, parent, -1, style=style )
        self.log = log
        self.rtc = rt.RichTextCtrl( self, style=wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER|rt.RE_READONLY )
        # wx.CallAfter( self.rtc.SetFocus )
        self.rtc.Freeze()
        self.rtc.BeginSuppressUndo()

        self.rtc.Newline()
        self.rtc.BeginTextColour((255, 0, 0))
        self.rtc.WriteText("Colour, like this red bit.")
        self.rtc.EndTextColour()

        self.rtc.EndSuppressUndo()
        self.rtc.Thaw()

        sizer = wx.BoxSizer( wx.VERTICAL )
        sizer.Add( self.rtc, 1, wx.EXPAND )

        self.SetSizer( sizer )


