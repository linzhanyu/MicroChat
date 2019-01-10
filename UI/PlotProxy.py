# -*- coding:utf-8 -*-
from __future__ import print_function

from config import UIConfig

# from pylab import mpl
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
from matplotlib.dates import *
import matplotlib.gridspec as gridspec

class PlotAdapter() :

    __glob_init_flag = False

    def __init__( self ):
        PlotAdapter.InitMatPlot()

    # Matplotlib 的一些全局性设置
    @staticmethod
    def InitMatPlot( self ):
        if PlotAdapter.__glob_init_flag:
            return
        # Global 设置
        # mpl.rcParams['font.sans-serif'] = ['SimHei'] #指定默认字体
        # mpl.rcParams['axes.unicode_minus'] = False #解决保存图像是负号'-'显示为方块的问题
        # mpl.rcParams['grid.color'] = 'r'

        PlotAdapter.__glob_init_flag = True

    def CreateFigure( self ):
        # self.bgColor = '#31312E'    # 黑色

        bgColor = UIConfig.bgColor
        edgeColor = UIConfig.edgeColor

        self.figure = Figure(facecolor=bgColor, edgecolor=edgeColor, tight_layout=False)
        self.figure.autofmt_xdate()
        self.canvas = FigureCanvas(self, -1, self.figure)
        # self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)

        outer_grid = gridspec.GridSpec(16,1) 
        outer_grid.update()
        left_cell = outer_grid[:10, :1]
        inner_grid = gridspec.GridSpecFromSubplotSpec( 16, 1, left_cell )

    # 划分格子

    # 在指定的格子中绘图

