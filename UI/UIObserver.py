# -*- coding:utf-8 -*-

from Observer import Observer
from LogicEvent import LogicEvt

class UIObserver( Observer ):
    def __init__( self ) :
        Observer.__init__(self)
        self.panels = []
        self.BindEvt( LogicEvt.UIDraw, self.OnDraw )

    def OnDraw( self, df ):
        # print( 'OnDraw', len(self.panels) )
        for panel in self.panels:
            # print( 'Draw:', panel )
            panel.draw( df )


