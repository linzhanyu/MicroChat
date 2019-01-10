# -*- coding:utf-8 -*-

import sys, datetime
from singleton import Singleton
if sys.version_info >= (3, 5):
    from DataSource import TushareDS, TDX_DB, TDX_DS, GM_DS
else:
    from DataSource import TushareDS, TDX_DB, TDX_DS
import DataSource
from DataSM import *
from DataCache import *
from Observer import Subject
# 先写这儿吧
from UIObserver import UIObserver

class DataMngr(Singleton):
    sm = DataSM()
    subject = Subject()
    localDB = TDX_DB()
    basicDS = TushareDS()
    mainDS  = GM_DS()
    fastDS  = TDX_DS()
    __inited = False
    def __init__( self ):
        # 虽然ID相同,但是这些 __init__ 会被多次调用
        # self.basicTable = None

        # for name in dir( DataSource ):
        #     print( name )
        if not DataMngr.__inited :
            self.basicTable = None
            self.ob_ui = UIObserver()
            # DataMngr.subject.Register( TushareDS() )
            # DataMngr.subject.Register( TDX_DS() )
            DataMngr.subject.Register( self.ob_ui )
            # DataMngr.subject.Register( GM_DS() )
            DataMngr.__inited = True
            self.memCache = MemoryDataCache( 10 )
            self.diskCache = DiskDataCache()


    def SetBasicTable( self, table ):
        self.basicTable = table;

    def AddBar( *params ):
        pass

    @staticmethod
    def __LoadFromCacheChain( code, ktype, start, end, rtype, query ):
        mngr = DataMngr()
        # 检查内存是否有缓存
        df = mngr.memCache.GetKBarDF( code, ktype, start, end, rtype, query )
        if df is not None:
            return df

        # 尝试加载硬盘存档

        # 远程加载

        # 更新硬盘存档

        df = DataMngr.basicDS.Get( ktype, code )
        # mngr.memCache.Cache( df, 
        return df



    @staticmethod
    def GetBasics():
        mngr = DataMngr()
        kTypeName = 'DAY'
        code, kname, start, end, rtype, query = 'basics', 'DAY', -1, -1, 'bfq', None
        df = mngr.memCache.GetKBarDF( code, kname, start, end, rtype, query )
        if df is not None:
            return df

        # 尝试加载硬盘存档
        dbFile = Common.TileDBFile( code )
        if os.path.exists( dbFile ) :
            modify = datetime.datetime.fromtimestamp( os.stat(dbFile).st_mtime )
            curtime = datetime.datetime.now()
            difftime = curtime - modify
            # print( type(difftime), difftime.days )
            if difftime.days < 1:
                df = mngr.diskCache.GetKBarDF( code, kname, start, end, rtype, query )
                return df

        try:
            df = DataMngr.basicDS.GetBasics()
            df.to_hdf( dbFile, code )
            mngr.diskCache.Cache( df, code, kname, start, end, rtype )
        except:
            print( '-' * 60 )
            df = DataMngr.mainDS.GetBasics()
            print( df.index )
            df.index = [DataMngr.mainDS.stockCodeName(idx) for idx, in df.index.values]
            print( df )
        
        return df

    @staticmethod
    def GetIndexs():
        df = DataMngr.mainDS.GetIndexs()
        df.index = [DataMngr.mainDS.stockCodeName(symbol) for symbol in df.index.values]
        return df

    @staticmethod
    def GetKBarDF( code, ktype, start=-1, end=-1, rtype='bfq', query=None ):
        '''
        code : 证券代码 sh600000 / sz000001
        ktype: K线类型 同通达信
        start: 开始时间
        end  : 结束时间
        rtype: 复权类型

        '''
        # 参数错误
        if not rtype in ['bfq', 'qfq', 'hfq', ]:
            return None

        # 未实现
        if rtype == 'qfq':
            return None

        # print( '=' * 60 )
        mngr = DataMngr()
        df = mngr.memCache.GetKBarDF( code, ktype, start, end, rtype, query )
        if df is None:
            df = mngr.diskCache.GetKBarDF( code, ktype, start, end, rtype, query )
            # TODO : 打开注释 将重写后复权数据
            # df = None
            if df is None:
                # 现在只能算一个新的.
                df = mngr.localDB.Get( ktype, code )
                if df is None:
                    print( 'Load hdf5 failed.', code, file = sys.stderr )
                elif df is not None and rtype != 'bfq':
                    df = df.ix[ (df.volume > 0.0) & (df.index >= '1990-01-01') ]
                    # TODO : 还没有复权就存盘了
                    if rtype == 'hfq':
                        # TODO : 需要处理的部分
                        # 此处复权数据的重新设计:从localDB中一致取复权数据
                        # 复权数据的更新由数据更新步骤完成

                        begTimeStr = '1990-01-01'
                        curTime = datetime.datetime.now()
                        endTimeStr = curTime.strftime('%Y-%m-%d')
                        rdf = mngr.mainDS.GetDivident( code, begTimeStr, endTimeStr, False )
                        if rdf is not None:
                            # rdf = Common.LoadRTable( code )
                            # 检查保留是为了兼容 TDX 的复权数据表
                            if '保留' in rdf.columns:
                                rdf = rdf[ rdf.保留 == 1 ]
                            # rdf.to_csv( 'rdf.csv' )
                            hfq_df = Common.calcHFQ_DF( df, rdf )
                            # TODO : 暂时禁用缓存待分钟数据校验正确后再启用
                            mngr.diskCache.Cache( hfq_df, code, ktype, start, end, rtype )
                            # df.to_csv( 'bfq.csv' )
                            df = hfq_df
                            # df.to_csv( 'hfq.csv' )
                    elif rtype == 'qfq':
                        raise 0
            else:
                # print( 'Mem Cache.' )
                mngr.memCache.Cache( df, code, ktype, start, end, rtype )

        # print( df.tail(5) )
        # 暂时读入时还是别去重了 会导致数据变少
        # if df is not None:
        #     df = df.drop_duplicates()
        return df



