# -*- coding:utf-8 -*-
from __future__ import print_function
import platform,subprocess, codecs, os, sys

def StartupSubProcess( cmd, run_dir, cb_line_proc, ex=True ):
    # default_encoding = 'utf-8'
    # if sys.getdefaultencoding() != default_encoding:
    #     reload(sys)
    #     sys.setdefaultencoding(default_encoding)

    print( 'Run dir : %s' % ( os.path.abspath(run_dir) ) )
    print( ' '.join(cmd) )
    newEnv = os.environ.copy()
    newEnv['LC_MESSAGES'] = 'en'
    try:
        if platform.system() == 'Windows':
            if ex:
                info = subprocess.STARTUPINFO()
                info.wShowWindow = False
                info.dwFlags=subprocess.SW_HIDE

                p = subprocess.Popen(cmd, env=newEnv, cwd=run_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, startupinfo=info, shell=True)
            else:
                p = subprocess.Popen(cmd, env=newEnv, cwd=run_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            p = subprocess.Popen(cmd, env=newEnv, cwd=run_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except OSError as e:
        print( 'Execute %s failed.' % (cmd[0],) )
        raise e

    # print( 'Callback line func : ', cb_line_proc )
    for line in iter(p.stdout.readline, b''):
        if cb_line_proc != None:
            # print( line )
            l = line
            try:
                # l = line.decode( 'GB18030' ).encode('utf-8')
                # l = unicode(line.decode('latin1')).encode('utf-8') # , 'ignore')
                l = line.decode('utf-8')
            except UnicodeDecodeError as e:
                try:
                    l = line.decode('gbk')
                except UnicodeDecodeError as e:
                    print( l, file=sys.stderr )
                    raise e
            l = l.replace( u'\r', u'' )
            l = l.replace( u'\n', u'' )
            cb_line_proc( l )
    ret = p.returncode
    if ret is None :
        ret = 0
    # 有些程序依赖于进程的输出，不要给 cb_line_proc 添加东西
    print( 'Process return : %s %s'% (str(p.returncode), str(ret) ) )
    return ret

