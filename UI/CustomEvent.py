# -*- coding:utf-8 -*-

import wx
import wx.lib.newevent

# ============================================================
# UI Event
# ============================================================
# 
# clientEVT_TASK_FINISH = wx.NewEventType()
# EVT_TASK_FINISH = wx.PyEventBinder( clientEVT_TASK_FINISH, 1 )
(clientEVT_TASK_FINISH, EVT_TASK_FINISH) = wx.lib.newevent.NewEvent()
(clientEVT_TASK_START,  EVT_TASK_START) = wx.lib.newevent.NewEvent()

