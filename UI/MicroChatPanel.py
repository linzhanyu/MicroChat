# -*- coding:utf-8 -*-
from __future__ import print_function

from config import Config
from LogicEvent import LogicEvt
from TaskMicroChat import MicroChat
import wx, wx.media
import os, sys, logging, re
from datetime import datetime

class MicroChatPanel( wx.Panel ):
    def __init__( self, parent, style, log ):
        wx.Panel.__init__( self, parent, -1, style=style )

        # self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.box_friend = box = wx.ListBox( self, wx.ID_ANY )
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add( box, 1, wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM | wx.EXPAND, 5)
        msizer = wx.BoxSizer( wx.VERTICAL )
        self.box_voice = box = wx.ListBox( self, wx.ID_ANY, style=wx.LB_MULTIPLE )
        msizer.Add( box, 1, wx.ALL | wx.EXPAND, 5 )
        sizer.Add( msizer, 2, wx.EXPAND )

        rsizer = wx.BoxSizer( wx.VERTICAL )
        sizer.Add( rsizer, 0, wx.EXPAND )

        # btn = wx.Button( self, -1, u'Create Bundle', name='bundleCreate' )
        btn_SyncFriends = wx.Button( self, wx.ID_ANY, u'Sync Friend', name='syncFriend' )
        btn_SyncAvatar = wx.Button( self, wx.ID_ANY, u'Sync Avatar', name='syncAvatar' )
        btn_SyncVoice = wx.Button( self, wx.ID_ANY, u'Sync Voice', name='syncVoice' )
        # btn_Listen = wx.Button( self, wx.ID_ANY, u'Listen', name='listen' )
        btn_Amr2Mp3 = wx.Button( self, wx.ID_ANY, u'To MP3', name='toMP3' )
        btn_JoinMp3 = wx.Button( self, wx.ID_ANY, u'Join MP3', name='joinMP3' )
        # player = wx.media.MediaCtrl( self, szBackend=wx.media.MEDIABACKEND_GSTREAMER )
        # msizer.Add( player, 0, wx.ALL | wx.EXPAND, 5 )

        rsizer.Add( btn_SyncFriends, 0, wx.EXPAND )
        rsizer.Add( btn_SyncAvatar, 0, wx.EXPAND )
        rsizer.Add( btn_SyncVoice, 0, wx.EXPAND )
        rsizer.Add( btn_Amr2Mp3, 0, wx.EXPAND )
        rsizer.Add( btn_JoinMp3, 0, wx.EXPAND )
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

        self.Bind( wx.EVT_BUTTON, self.OnSyncFriends, btn_SyncFriends )
        self.Bind( wx.EVT_BUTTON, self.OnSyncAvatar, btn_SyncAvatar )
        self.Bind( wx.EVT_BUTTON, self.OnSyncVoice, btn_SyncVoice )
        self.Bind( wx.EVT_BUTTON, self.OnToMP3, btn_Amr2Mp3 )
        self.Bind( wx.EVT_BUTTON, self.OnJoinMP3, btn_JoinMp3 )
        self.Bind( wx.EVT_LISTBOX, self.OnSelFriend, self.box_friend )
        self.Bind( wx.EVT_LISTBOX_DCLICK, self.OnListen, self.box_voice )

        self.InitLocalData()

    def InitLocalData( self ):
        self.__GetIMEI_UNI()
        friends = self.__GetContactPath( False )
        self.__RefreshVoiceDic()
        self.__SetFriends( friends )
        # for friend in friends:
        #     username, alias, nickname, usertype = friend
        #     userHash = MicroChat.GetHash( username, '' )[:7]
        #     if userHash in self.voiceDic:
        #         self.box_friend.Append( nickname, friend )


    def OnSyncFriends( self, event ):
        self.__GetIMEI_UNI()
        friends = self.__GetContactPath( True )
        if friends != None:
            self.__SetFriends( friends )

    def __RefreshVoiceDic( self ):
        voiceDir = 'data/voice2'
        self.voiceDic = {}
        if os.path.exists( voiceDir ):
            voiceList = self.ListDir( voiceDir )

            # print( len(voiceList) )
            voiceDic = self.voiceDic
            p = re.compile(r'msg_([0-9a-f]{6})([0-9a-f]{6})([0-9a-f]{7})([0-9a-f]{7}).amr')
            for f, r in voiceList:
                m = p.match( f )
                if m is not None:
                    # print( f )
                    user_hash = m.group(3)
                    if user_hash in voiceDic:
                        voiceDic[user_hash].append( (f, r) )
                    else:
                        voiceDic[user_hash] = [(f, r), ]

    def __SetFriends( self, friends ):
        self.box_friend.Clear()
        for friend in friends:
            username, alias, nickname, usertype = friend
            userHash = MicroChat.GetHash( username, '' )[:7]
            if userHash in self.voiceDic:
                self.box_friend.Append( nickname, friend )

    def OnSyncAvatar( self, event ):
        MicroChat.PullAvatar( self.hashName )

    def OnSyncVoice( self, event ):
        MicroChat.PullVoice( self.hashName )
        self.__RefreshVoiceDic()
        friends = self.__GetContactPath( False )
        if friends != None:
            self.__SetFriends( friends )

    def OnListen( self, event ):
        # 转换amr -> temp/*.mp3
        # wx.media.MediaCtrl
        print( 'Listen' )
        pass

    def OnToMP3( self, event ):
        print( 'To MP3' )
        selist = self.box_voice.GetSelections()
        if len(selist) == 0:
            return
        for amr in selist:
            f, r = self.box_voice.GetClientData( amr )
            amrPath = '%s/%s' % (r, f)
            mp3Path = os.path.splitext(amrPath)[0] + '.mp3'
            if not os.path.exists( mp3Path ):
                MicroChat.ConvMP3( amrPath )

    def OnJoinMP3( self, event ):
        print( 'Join MP3' )
        selist = self.box_voice.GetSelections()
        if len(selist) < 2:
            return

        files = []
        for amr in selist:
            f, r = self.box_voice.GetClientData( amr )
            amrPath = '%s/%s' % (r, f)
            mp3Path = os.path.splitext(amrPath)[0] + '.mp3'
            if not os.path.exists( mp3Path ):
                MicroChat.ConvMP3( amrPath )
            files.append( mp3Path )

        ifriend = self.box_friend.GetSelection()
        friend = self.box_friend.GetClientData( ifriend )
        username, alias, nickname, usertype = friend

        b, r = self.box_voice.GetClientData( selist[0] )
        e, r = self.box_voice.GetClientData( selist[-1] )
        out_name = 'join_%s_%s%s%s_%s%s%s-%s%s%s_%s%s%s' % (
                nickname,
                b[14:16], b[10:12], b[12:14], b[6:8], b[4:6], b[8:12],
                e[14:16], e[10:12], e[12:14], e[6:8], e[4:6], e[8:12], )

        MicroChat.JoinMP3( files, out_name )

    def OnSelFriend( self, event ):
        # print( event.GetSelection(), event.GetInt(), event.GetString(), event.GetClientData() )
        friend = event.GetClientData()
        username, alias, nickname, usertype = friend
        self.__RefreshVoiceList( username )

    def __GetIMEI_UNI( self ):
        IMEI = Config.IMEI
        IMEI2= Config.IMEI2
        UNI  = Config.UNI

        self.imeis = MicroChat.GetIMEI()
        print( '-' * 5, self.imeis )
        if len( self.imeis ) == 0:
            self.imeis.append( IMEI )
            self.imeis.append( IMEI2 )
        self.uni = MicroChat.GetUNI()
        if self.uni == '':
            self.uni = UNI
        # self.hashName = MicroChat.GetHash( self.imeis[0], self.uni )
        self.hashName = MicroChat.GetHash( 'mm', self.uni )

    def __GetPWD( self ):
        pwds = []
        imeis, uni = (self.imeis, self.uni)
        for imei in imeis:
            pwd = MicroChat.GetDBPwd( imei, uni )
            pwds.append( pwd )
        return pwds

    def __GetContactPath( self, force ):
        imeis, uni = (self.imeis, self.uni)

        pwds = self.__GetPWD()
        print( 'DEBUG:', uni, pwds[0] )
        # print( pwds )
        friends = MicroChat.GetContact( pwds[0], uni, force )
        return friends
        # return name

    def __RefreshVoiceList( self, username ):
        userHash = MicroChat.GetHash( username, '' )[:7]
        # print( userHash, len(self.voiceDic) )
        self.box_voice.Clear()
        if userHash in self.voiceDic:
            voiceList = self.voiceDic[userHash]
            dataList = []
            for f, r in voiceList:
                p = re.compile(r'msg_([0-9a-f]{6})([0-9a-f]{6})([0-9a-f]{7})([0-9a-f]{7}).amr')
                m = p.match( f )
                if m is not None:
                    # print( f )
                    time_str = m.group(1)
                    date_str = m.group(2)
                    user_str = m.group(3)
                    time_text = '%s:%s:%s' % ( time_str[2:4], time_str[0:2], time_str[4:6] )
                    date_text = '20%s-%s-%s' % ( date_str[4:6], date_str[0:2], date_str[2:4] )
                    dataList.append(['%s %s' % (date_text, time_text ), (f, r)])

            def SelFirst( element ):
                return element[0]
            dataList.sort( key=SelFirst, reverse=True )
            for text, data in dataList:
                self.box_voice.Append( text, data )

    @staticmethod
    def ListDir( local_dir ):
        fileList = [] # filename : filedir
        for root, dirs, files in os.walk( local_dir ):
            for f in files:
                fileList.append( (f, root) )
        return fileList

