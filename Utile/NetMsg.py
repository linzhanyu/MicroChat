# -*- coding:utf-8 -*-

import struct, sys
# LZ4 是最快速的压缩算法
import lzma, zlib, lz4
import binascii
import json
from singleton import Singleton
from MyEnum import Enum

'''
网络消息定义
类似的C数据结构
struct SNetMsg
{
    UINT16  m_id;
    UINT    m_size;
    char*   m_msg;
    UINT    m_crc32;
};
字节序：little-endian
'''

EMSG_ID = None

class MsgMng( Singleton ):
    def __init__( self ):
        self.msgDict = {}

    def BuildMsg( msgID ) :
        if msgID in self.msgDict.keys() :
            return self.msgDict[msgID]()
        return None

    @staticmethod
    def Register( msgID, buildFunc ):
        mng = MsgMng()
        mng.msgDict[msgID] = buildFunc

    @staticmethod
    def Unregister( msgID ) :
        mng = MsgMng()
        if msgID in self.msgDict.keys() :
            del mng.msgDict[msgID]

class EasyFlags:
    def __init__( self, validBit ):
        self.__byte = validBit / 8 + ((validBit % 8 != 0) and 1 or 0)
        self.__raw = 0

    def SetBit( self, idxBit, boolean ):
        if boolean == True :
            self.__raw |= 0x01 << idxBit
        else:
            self.__raw &= ~(0x01 << idxBit)

    def GetBit( self, idxBit ):
        return (self.__raw & (0x01 << idxBit)) != 0

    def GetRaw( self ):
        return self.__raw

    def SetRaw( self, value ):
        self.__raw = value

############################################################
# | 8b-flags | 16b-length | 16b-id | nB-data | 32b-CRC |
############################################################
MsgFlag = Enum(
        'Compress',
        )

class NetMsg :
    def __init__( self, msgID=0, compress=False ):
        self.msgID = msgID
        self.flags = EasyFlags(8)
        self.flags.SetBit( MsgFlag.Compress, compress )
        self.__data = {}

    def Pack( self ) :
        rawJson = self.PackData()
        nLen = len(rawJson)
        # print( 'Flags raw : ', self.flags.GetRaw() )
        rawData = bytearray( struct.pack( '<BHH%dsI'%(nLen,), self.flags.GetRaw(), self.msgID, nLen, rawJson, 0 ) )
        crc = binascii.crc32( rawData[:-4] )
        # print( self.msgID, nLen, rawJson, crc )
        struct.pack_into( 'I', rawData, -4, crc )
        # print( rawData )
        return rawData

    # 在这里可以添加数据压缩代码
    def PackData( self ):
        buf = json.dumps( self.__data )
        # print( buf )
        byteBuf = bytes( buf, encoding='utf-8' )
        # print( 'Flags raw : ', self.flags.GetBit( MsgFlag.Compress ) )
        if self.flags.GetBit( MsgFlag.Compress ) :
            byteBuf = self.CompressBytes( byteBuf )
        return byteBuf

    def UnpackData( self, byteData ):
        rawData = byteData
        if self.flags.GetBit( MsgFlag.Compress ) :
            rawData = self.DecompressBytes( byteData )
        data = str(rawData, encoding='utf-8')
        print( len(data) )
        self.__data = json.loads( data )
        for k, v in self.__data.items():
            setattr(self.__class__, k, v)
        print( self.__data )

    def CompressBytes( self, buf ) :
        # print( 'Compress' )
        # return lzma.compress( buf, format=lzma.FORMAT_ALONE, check=lzma.CHECK_NONE )
        # return zlib.compress( buf, 4 )
        return lz4.compress( buf )

    def DecompressBytes( self, buf ):
        # print( 'Decompress' )
        # return lzma.decompress( buf, format=lzma.FORMAT_ALONE )
        # return zlib.decompress( buf )
        return lz4.decompress( buf )

    def GetValue( self, key ):
        if key in self.__data.keys() :
            return self.__data[key]
        return None

    def SetValue( self, key, value ) :
        self.__data[key] = value
        setattr(self.__class__, key, value)

    @staticmethod
    def Unpack( rawData ):
        nData = len(rawData)
        msg = NetMsg()
        idx = 0
        try :
            rawFlags, msg.msgID, nLen = struct.unpack_from( '<BHH', rawData, idx )
            msg.flags.SetRaw( rawFlags )
            idx += 5
            rawJson, crc = struct.unpack_from( '<%dsI'%(nLen,), rawData, idx )
            print( 'Unpack : ', nLen, len(rawJson) )
            idx += nLen + 4
            newcrc = binascii.crc32(rawData[:idx-4])
            if binascii.crc32(rawData[:idx-4]) != crc :
                print( 'Error : ', msg.msgID, nLen, rawJson, crc, newcrc, file=sys.stderr )
                raise
            else:
                # print( msg.msgID, nLen )
                pass
            msg.UnpackData( rawJson )
        except struct.error as err :
            return None, None
        except RuntimeError as err :
            return None, None
        return msg, nLen

############################################################
# BuildServer -> MainServer
# Regist ==> [BuildType:(Android, IOS), OS:(Windows,MAC), Version:1.0, ]
# RetRegister <== 成功
# ExecTask ==> 执行任务 [ TaskID, Params ]
# StateNotify ==> [ State:(接受，准备环境，编译，传输，出错)]

class BMMsgRegistBuildServer( NetMsg ) :
    def __init__( self ):
        NetMsg.__init__( self, EMSG_ID.BM_REGIST_BUILD_SERVER, True )

    def SetAttribute( self, buildTypeVal, platformVal, processorVal, version ) :
        self.SetValue( 'BuildType', buildTypeVal )
        self.SetValue( 'Platform', platformVal )
        self.SetValue( 'Processor', processorVal )

class BMMsgRegistBuildServerRet( NetMsg ):
    def __init__( self ):
        NetMsgNull.__init__( self, EMSG_ID.BM_REGIST_BUILD_SERVER )

############################################################
# Client -> MainServer
# Login ==> 客户端版本号认证
# LoginRet <== 
# RequestServerList ==> 请求编译服务器状态
# RequestServerListRet <== 返回所有编译服务器当前状态 [ N, ((BSID, State),...) ]
# SubmitTask ==> [ Ver No., MiniClient, ]
# SubmitTaskRet <== 是否接受
# QueryTaskState ==> 查询任务执行状态
# QueryTaskStateRet <== 返回 [ TaskID, State, err_log, filePath ]
############################################################
def InitMsg() :
    global EMSG_ID
    if EMSG_ID != None :
        return

    EMSG_ID = Enum(
            'NONE',
            'BM_REGIST_BUILD_SERVER',       # 注册 Build 服务器
            'MB_REGIST_BUILD_SERVER_RET',   # 注册 Build 服务器 返回
            'MB_BUILDTASK',
            )
    mng = MsgMng()

    mng.Register( EMSG_ID.BM_REGIST_BUILD_SERVER,        lambda : MsgRegistBuildServer() )
    mng.Register( EMSG_ID.MB_REGIST_BUILD_SERVER_RET,    lambda : MsgRegistBuildServerRet() )

