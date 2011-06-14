#!/usr/bin/python
# -*- coding: utf-8 -*-

import mpd
import urllib
import sys
from ErrorsHandler import *

import  LoadConfig
config = LoadConfig.LoadConfig()


client = mpd.MPDClient()           # create client object
#client.stop()
#client.connect("localhost", 6600)  # connect to localhost:6600
#client.close()                     # send the close command
#client.disconnect() 


class OggPlayer:
    """MPD player client for BurnStation
    """

    def __init__(self):
        self._player = None

        self._playing      = False
        self._playlist    = []
        self._current     = -1
        self.volume_level = 0.5

        logger.info("MPD player init complete")

    def ClearPlaylist(self):
        self._playlist = []
        self._current = -1

    def AddToPlaylist(self, uri):
        basepath = 'file://' + config.musicPath + 'music/'
        uri = uri.replace(basepath, '')
        logger.info("OggPlayer.AddToPlayList trying to add: " + uri)
        client.connect("localhost", 6600)  # connect to localhost:6600
        client.clear()
        client.add(uri)
        client.close()                     # send the close command
        client.disconnect()
        logger.info("OggPlayer.AddToPlayList: " + uri)
        print("OggPlayer.AddToPlayList: " + uri)

    def Play(self):
        client.connect("localhost", 6600)  # connect to localhost:6600
        client.stop()
        client.play()
        client.close()                     # send the close command
        client.disconnect()

    def Stop(self):
        client.connect("localhost", 6600)  # connect to localhost:6600
        client.stop()
        client.close()                     # send the close command
        client.disconnect()

    def Seek(self, time):
        #os.popen('mpc seek +00:00:10')
        client.connect("localhost", 6600)  # connect to localhost:6600
        client.seek(0, time)
        client.close()                     # send the close command
        client.disconnect()

    def SetVolume(self, level):
        self.volume_level = level
        logger.info("player: setting volume to: %f" % level)

