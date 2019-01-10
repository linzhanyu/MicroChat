#!/usr/bin/env python
# cdoing:utf-8
import urllib,sys,optparse,sys
p=optparse.OptionParser("%prog -f Contacts -m MessAge",version='1.0',prog="SendRTX.py",epilog='http://bbs.linuxtone.org')
p.add_option('-f','--filename',dest='Filename',help='filename Contains Contacts')
p.add_option('-m','--message',dest='Message',help='Message Sent To  Contacts')
p.add_option('-s','--server',dest='server',help='RTX SDK SERVER')
p.add_option('-u','--userlist',dest='userlist',help='UserList split by ",",do not use with -f')
if len(sys.argv)==1:
    p.print_help()
    sys.exit(1)
opt,args=p.parse_args()

if not opt.Message or     (opt.Filename and opt.userlist)  or not opt.server or not (opt.Filename or opt.userlist) :
    p.print_help()
    sys.exit(1)

def transcode(stotrans):
    return stotrans.decode('utf-8').encode('gb2312')

if opt.Filename:
    try:
        reciver=','.join(open(opt.Filename).read().splitlines())
    except IOError,e:
        print e
        sys.exit(1)
else:
    reciver=opt.userlist

server=opt.server
Title=transcode('linzhanyu')
if sys.platform == 'win32':
    reciver=reciver
    MESSAGE=opt.Message+' '+' '.join(args)
else:        
    reciver=transcode(reciver)
    MESSAGE=transcode(opt.Message+' '+' '.join(args))
urllib.urlopen('http://'+server+'/sendnotify.cgi?msg='+MESSAGE+'&receiver='+reciver+'&title='+Title)
