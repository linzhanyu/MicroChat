# -*- coding:utf-8 -*-

import logging, re, hashlib, os
from Process import StartupSubProcess
from pysqlcipher3 import dbapi2 as sqlite3
# 微信处理相关任务

class MicroChat:
    PullCB = None
    PushCB = None

    @staticmethod
    def GetIMEI():
        imeis = []
        p = re.compile( r'(\d+)\s*' )
        def ProcIMEI( line ):
            imei = line.strip()
            
            print( imei )
            if 'error:' not in imei and len(imei) > 0:
                imeis.append( imei )
        StartupSubProcess( ['shell/get_android_imei.sh', ], '.', ProcIMEI )
        return imeis

    @staticmethod
    def GetUNI():
        uni = []
        def ProcUNI( line ):
            r = r'^\s*<int name="_auth_uin" value="(\d+)" />'
            pattern = re.compile( r )
            m = pattern.match( line )
            if m is not None:
                uni.append( m.group(1) )
            
        StartupSubProcess( ['shell/get_android_prefs.sh', ], '.', ProcUNI )
        return len(uni) > 0 and uni[0] or ''

    @staticmethod
    def GetDBPwd( imei, uni ):
        return MicroChat.GetHash( imei, uni )[:7]

    @staticmethod
    def GetHash( prefix, uni ):
        prefix = bytes(prefix,encoding='utf-8')
        uni = bytes(uni,encoding='utf-8')
        return hashlib.md5( prefix + uni ).hexdigest()

    @staticmethod
    def SetENV( value ):
        print( 'ENV:', 'USER_HASH', value )
        os.environ.putenv( 'USER_HASH', value )

    @staticmethod
    def GetContact( pwd, uni, force ):
        '''解析联系人列表'''
        if force :
            MicroChat.PullContact( 'mm', uni )

        ret = MicroChat.ReadContact( 'data/EnMicroMsg.db', pwd )
        return ret

    def ReadContact( dbPath, pwd ):
        db = sqlite3.connect( dbPath )
        c = db.cursor()
        c.execute('pragma key="%s";' % (pwd, ) )
        c.execute("PRAGMA cipher_use_hmac = OFF;")
        c.execute("PRAGMA cipher_page_size = 1024;")
        c.execute("PRAGMA kdf_iter = 4000;")
        # result = db.execute("PRAGMA cipher_migrate;" )
        result = []
        
        try:
            rc = c.execute( 'select username, alias, nickname, type from rcontact where type&3==3' )
            result = rc.fetchall()
        except Exception as e:
            print( 'Failed.' )
            pass
        else:
            print( len(result) )
            # for item in result :
            #     print( item )
        finally:
            c.close()
            return result

    @staticmethod
    def PullFile( cmd ):
        cb = MicroChat.PullCB
        if cb is None:
            cb = logging.info
        StartupSubProcess( cmd, '.', cb )

    @staticmethod
    def PullContact( imei, uni ):
        '''传输联系人数据'''
        hashName = MicroChat.GetHash( imei, uni )
        MicroChat.SetENV( hashName )
        MicroChat.PullFile( ['shell/get_contact.sh', hashName] )

    @staticmethod
    def PullAvatar( hashName ):
        '''传输头像数据'''
        MicroChat.PullFile( ['shell/get_avatar.sh', hashName ] )

    @staticmethod
    def PullVoice( hashName ):
        '''传输语音数据'''
        MicroChat.PullFile( ['shell/get_voice2.sh', hashName] )

    @staticmethod
    def ConvMP3( amrPath ):
        amrPath = os.path.abspath( amrPath )
        print( amrPath )
        StartupSubProcess( ['shell/amr_2_mp3.sh', amrPath], '.', logging.info )

    @staticmethod
    def JoinMP3( files, outfile ):
        param = '|'.join( files )
        StartupSubProcess( ['shell/join_mp3.sh', param, outfile], '.', logging.info )


