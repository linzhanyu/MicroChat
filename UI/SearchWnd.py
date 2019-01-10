# -*- coding:utf-8 -*-
import wx

class SearchWnd( wx.Window ):
    def __init__( self, parent, id, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, name=wx.PanelNameStr ):
        wx.Window.__init__( self, parent, id, pos, size, style, name )

        title = wx.StaticText(self, wx.ID_ANY, 'Search', style=wx.TE_CENTER)
        text  = wx.TextCtrl(self, wx.ID_ANY, '')
        box   = wx.ListBox(self, wx.ID_ANY)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(title, 0, wx.BOTTOM | wx.EXPAND, 10)
        sizer.Add(text, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(box, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 5)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

        self.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)
        text.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        box.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        text.Bind(wx.EVT_TEXT, self.OnText)

        self.text = text
        self.box  = box

    def OnSetFocus(self, evt):
        self.text.SetFocus()
        evt.Skip()

    def OnText(self, evt):
        text = self.text.GetLineText(0)
        # self.text.Clear()
        self.text.ChangeValue(text.upper())
        self.text.SetInsertionPoint(len(text))
        evt.Skip()

    def OnKeyDown(self, evt):
        from ClientFrame import Frame
        if evt.GetKeyCode() == wx.WXK_ESCAPE and Frame.mainFrame is not None:
            Frame.mainFrame.HideSearchWnd()
        if evt.GetKeyCode() in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER) and Frame.mainFrame is not None:
            Frame.mainFrame.HideSearchWnd()
            # print(evt.GetKeyCode(), Frame.mainFrame)
        evt.Skip()
        
    def Init(self, txt):
        self.text.Clear()
        self.text.WriteText(txt)

