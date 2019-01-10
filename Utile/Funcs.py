# -*- coding:utf-8 -*-

'''
实现一些常用的 TDX / THS 公式中的方法
'''

import numpy as np
import talib
import functools

def LLV( v, n ):
    size = len(v)
    # result = np.full( size, 0, dtype=np.float64 )
    result = v.copy()

    # for i in range( n ):
    #     result[i] = v[i]

    for i in range( n, size, 1 ):
        sub = v[i-n : i]
        result[i] = sub.min()
    return result

def HHV( v, n ):
    size = len(v)
    # result = np.full( size, 0, dtype=np.float64 )
    result = v.copy()

    # for i in range(n):
    #     result[i] = v[i]

    for i in range( n, size, 1 ):
        sub = v[i-n : i]
        result[i] = sub.max()
    return result

def MA( v, n ):
    # 计算均线需要使用 0 类型的 如果其它指标需要请新建其它函数
    size = len(v)
    result = np.full( size, 0, dtype=np.float64 )
    result = talib.MA(v, n, 0)
    if n > 1:
        for i in range( n - 1 ):
            result[i] = v[i]
    return result

def SMA( v, n, m ):
    # return talib.SMA( v, n )
    # return talib.MA( v, n-1, 1 )
    size = len(v)
    # result = np.full( size, 0, dtype=np.float64 )
    result = v.copy()
    # vv = v.copy()

    # print( result )
    # ma = talib.MA(v, n)
    # vv[:n] = ma[:n]
    for i in range( n - 1 ):
        result[i] = 0
    for i in range( n, size, 1 ):
        # print( '({} * {} + {} * ({}-{})) / {} '.format(\
        #         ma[i], m, result[i-1], n, m, n ) )
        # sub = v[i-n : i]
        # result[i] = ((sub.sum()/n)*m + result[i-1] * (n-m)) / n
        result[i] = ((v[i]*m) + (result[i-1]*(n-m))) / n
        # result[i] = ((v[i]) + (result[i-1]*(n-m))) / n
    return result

def EMA( v, n ):
    '''
    EMA / SMA 函数不是简单的 SUM(X1: Xn) / n
    统一的数字依赖于数据起始点的统一
    '''
    return talib.MA(v, timeperiod=n, matype=1)
    # return talib.EMA(v, timeperiod=n)
    # 这两句结果相同
    # return SMA( v, n+1, 2 )

def EXPMEMA( v, n ):
    # return talib.MA( v, n, 2 )
    # return talib.WMA( v, n )
    return SMA( v, n+1, 2 )

def STD( v, n ):
    return talib.STDDEV( v, n )

def AVEDEV( v, n ):
    '''平均绝对偏差'''
    pass

def MAX( v1, v2 ):
    return np.maximum( v1, v2 )

def POW( v, exp ):
    return np.power( v, exp )

def SUM( v, n ):
    size = len(v)
    result = v.copy()

    if n == 0:
        for i in range(1, size, 1):
            result[i] = result[i-1] + v[i]
    else:
        for i in range(n, size, 1):
            sub = v[i-n:i]
            result[i] = np.sum(sub)
    return result

def COUNT( v, n ):
    size = len(v)
    r = np.full( size, 0, dtype=np.int32 )
    if n > 0:
        for i in range( n, size, 1 ):
            r[i] = np.count_nonzero(v[i-n:i])
    # print( r )
    return r

def SQRT( v ):
    ret = np.sqrt( v )
    ret = np.nan_to_num( ret )
    return ret

def ABS( v ):
    return np.abs( v )


def REF( v, n ):
    size = len(v)
    ret = v.copy()
    if n > 0:
        ret[n:] = v[:size-n]
        # for i in range( n, size, 1 ):
        #     ret[i] = v[i-n]
    elif n < 0:
        ret[:n] = v[-n:size]
        # for i in range( 0, size+n, 1 ):
        #     ret[i] = v[i-n]

    return ret

def IF(condition, true_statement, false_statement):
    return np.where( condition, true_statement, false_statement )
    # 这个不能用
    # return true_statement if condition else false_statement

def IFV( func, *args ):
    vfunc = np.vectorize( func )
    return vfunc( *args )

#============================================================
def cross_detect( detect_func, alive, base ):
    n = len(alive)
    ret = np.zeros(n, dtype=np.bool)
    for i in range(1, n, 1):
        ret[i] = detect_func(alive[i-1:i+1], base[i-1:i+1])
    return ret

def UCross( alive, base ):
    '''
    d 线上穿 b 线
    '''
    def detect( a, b ):
        return a[-2] < b[-2] and a[-1] > b[-1]
    return cross_detect( detect, alive, base )

def DCross( alive, base ):
    '''
    d 线下穿 b 线
    '''
    def detect( a, b ):
        return a[-2] > b[-2] and a[-1] < b[-1]
    return cross_detect( detect, alive, base )

# ef ROSE( C ):
#    '''
#    帐幅
#    '''
#    rose = (C - REF(C, 1)) / REF(C, 1)
#    return rose

def ROSE( df ):
    '''
    涨幅
    '''
    CLOSE = df.close.values
    rose = (CLOSE - REF(CLOSE, 1)) / REF(CLOSE, 1)
    return rose

