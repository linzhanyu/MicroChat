# -*- coding:utf-8 -*-
# 状态机

from MyEnum import Enum

SMState = Enum(
        'INIT',
        'RUNING',
        'STOP',
        'ERROR',
        )

class StateMachine:
    def __init__(self):
        self.curIdx = 0
        self.smList = [(NoneState(), 0, 0, ), ]
        # self.smList.append( other sm )

    def Start( self ):
        while True:
            curSM, rightIdx, errorIdx = self.smList[self.curIdx]
            # print( 'State final ', self.curIdx )
            if curSM.State() == SMState.STOP :
                self.Next()
            else:
                break

    def __startNextState( self, nextIdx ):
        if nextIdx >= 0 and nextIdx < len(self.smList) :
            self.curIdx = nextIdx
            nextSM = self.smList[nextIdx][0]
            nextSM.Reset()
            nextSM.Start()

    def Next(self):
        # print( 'Next state.' )
        curSM, rightIdx, errorIdx = self.smList[self.curIdx]
        if curSM.State() == SMState.STOP:
            self.__startNextState( rightIdx )
        elif curSM.State() == SMState.ERROR:
            self.__startNextState( errorIdx )




        

class StateMachineState:
    def __init__(self):
        self.state = SMState.INIT

    def Start(self):
        self.state = SMState.RUNING
        try:
            ret = self.OnStart()
            self.state = ret and SMState.STOP or SMState.ERROR
        except Exception as e:
            self.state = SMState.ERROR
            raise e
        finally:
            self.state = SMState.STOP

    def OnStart( self ):
        return True

    def State(self):
        return self.state

    def Reset( self ):
        self.state = SMState.INIT

class NoneState( StateMachineState ):
    def State( self ):
        return SMState.STOP

class FinalState( StateMachineState ):
    def State( self ):
        return SMState.ERROR

