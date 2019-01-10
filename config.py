# -*- coding:utf-8 -*-
import platform

g_version = (0,0,0,1)

def GetMySQLLib():
    import sys
    if sys.version_info.major == 2:
        return 'mysqldb'
    elif sys.version_info.major == 3:
        return 'pymysql'
    else:
        ''

class Config :
    # * ADK 路径 如 D:/android/android-sdk
    ADK     = platform.system() == 'Windows' and r'D:\Android\SDK' or '/mnt/disk/android/Android/Sdk'
    # 编译日志文件
    LogFile = 'MicroChat.log'
    # Python3 可执行程序的路径
    python3 = platform.system() == 'Windows' and r'D:\Python34\python.exe' or 'python3'
    IMEI = ''
    IMEI2= ''
    UNI  = ''

class UIConfig:
    bgColor     = '#000000'    # 黑色
    edgeColor   = '#FF0000'    # 红色

__all__ = ['Config', 'UIConfig', ]

