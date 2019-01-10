# -*- coding:utf-8 -*-
import hashlib
from pysqlcipher3 import dbapi2 as sqlite3
from playhouse.sqlcipher_ext import *

IMEI = b'867977034738949'
IMEI2= b'867977034738956'
DID  = b'2CDF886C171CF648'
UNI  = b'1841634900'

def Pwd( imei, uni ):
    buf = imei + uni
    m = hashlib.md5( buf )
    hashStr = m.hexdigest()
    print( hashStr )
    # return hashStr
    return hashStr[:7]

def ReadContact( dbPath, pwd ):
    db = sqlite3.connect( dbPath )
    c = db.cursor()
    # print( 'pragma key="%s";' % (pwd, ) )
    result = c.execute('pragma key="%s";' % (pwd, ) )
    c.execute("PRAGMA cipher_use_hmac = OFF;")
    c.execute("PRAGMA cipher_page_size = 1024;")
    c.execute("PRAGMA kdf_iter = 4000;")
    # result = db.execute("PRAGMA cipher_migrate;" )
    
    # db.commit()
    # print( result )
    try:
        # rc = c.execute( 'select * from rcontact' )
        # rc = c.execute( 'pragma table_info(rcontact)' )
        # rc = c.execute( 'select username, alias, nickname, type, openImAppid from rcontact where type==3' )
        # rc = c.execute( 'select username, alias, nickname, type, contactLabelIds, descWordingId, openImAppid from rcontact where type&3==3' )
        rc = c.execute( 'select username, alias, nickname, type from rcontact where type&3==3' )
        # rc = c.execute( 'select * from rcontact where alias=="Ppwave"' )
        result = rc.fetchall()
    except Exception as e:
        print( 'Failed.' )
        pass
    else:
        print( len(result) )
        for item in result :
            print( item )
        # print( 'SELECT ', result )
    finally:
        c.close()

############################################################
# md5( username ) => user id
# user id 可以用来索引匹配 头像 / 语音
############################################################
    # db = SqlCipherDatabase(dbPath, passphrase=pwd)
    # try:
    #     result = db.execute( 'select * from rcontact' )
    # except Exception as e:
    #     print( 'Failed.' )
    #     pass
    # else:
    #     print( 'SELECT ', result )
    # finally:
    #     db.close()

    

if __name__ == '__main__':
    print( '-' * 70 )
    # imeis = [IMEI, IMEI2, b'mm', ]
    # for imei in imeis :
    #     pwd = Pwd( imei, UNI )
    #     ReadContact( 'MicroMsg/1f80eda3ed2cbfc71e2d42e08788430b/EnMicroMsg.db', pwd )
    #     ReadContact( 'MicroMsg/daa718297077368bcc5adcf738738d79/EnMicroMsg.db', pwd )
    pwd = Pwd( IMEI, UNI )
    ReadContact( 'MicroMsg/daa718297077368bcc5adcf738738d79/EnMicroMsg.db', pwd )
        

