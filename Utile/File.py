# -*- coding:utf-8 -*-

import json

def load_file( path ):
    c = ''
    f = open( path, 'r' )
    c = f.read()
    f.close()
    return c

def save_file( path, data ):
    f = open( path, 'w' )
    f.write( data )
    f.flush()
    f.close()

def save_file_json( path, dataDict ):
    save_file( path, json.dumps(dataDict, indent=4, encoding="utf-8") )

