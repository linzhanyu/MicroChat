# -*- coding:utf-8 -*-

from MyEnum import Enum

LogicEvt = Enum(
        'UpdateBasics',
        'UpdateHistory',
        'LoadData',
        'RealtimeBar',
        'RealtimeTick',
        'UIDraw',
        )

ThreadEvt = Enum(
        'NONE',         # 无效事件

        'SERVICE_START',# Service 启动
        # Service -> BackTest
        'SERVICE_READY',# A 服务线程准备就绪
        'TICK',         # A Tick 数据收到
        'BAR',          # A Bar  数据收到
        'ORDER',        # B 订单反馈
        'TRADE',        # A 成交反馈 --> ORDER

        # BackTest -> Service 
        'TICK_RET',     # B Tick 数据计算完成
        'BAR_RET',      # B Bar  数据计算完成
        'ORDER_CREATE', # B 取消订单
        'ORDER_CANCEL', # B 取消订单
        'FINISH',       # B 策略完成

        'COUNT',        # 事件总数计数
        )



