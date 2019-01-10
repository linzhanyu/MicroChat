# -*- coding:utf-8 -*-

def DebugLog( msg ):
    import wx
    msg = msg.replace(u'\r', u'')
    msg = msg.replace(u'\n', u'')
    wx.LogDebug( msg )

