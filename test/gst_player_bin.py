#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib  
import pygst  
pygst.require("0.10")
import sys, gst, gobject
import gtk
from MiscTools import *
from ErrorsHandler import *
gobject.threads_init()  

class OggPlayer:
    """GStreamer Based audio player for BurnStation
    
    This use the python GStreamer module to play the music from
    the burnstation.

    In order to work you need gst-python installed
    """

    def __init__(self):
        self._player = None

        self._playing = False
        self._playlist = []
        self._current = -1
        logger.info("GST init complete")

    def ClearPlaylist(self):
        self._playlist = []
        self._current = -1

    def AddToPlaylist(self, uri):
        self.uri = uri
        logger.info("Added " + uri)
        self._playlist.append(uri)

    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            logger.info("Error: %s" % err, debug)
            self.Stop()
        elif t == gst.MESSAGE_EOS:
	    self.Stop()
            self._current += 1
	    if self._current >= len(self._playlist):
		self.current = -1
	    else:
		self.Play()
            logger.info('End of stream')
	return True

    def Play0(self, uri):
        player = gst.element_factory_make("playbin", "player")

        print 'Playing:', uri
        player.set_property('uri', uri)
        player.set_state(gst.STATE_PLAYING)


    #def Play(self):
        self.Stop()
        #uri = QuoteForPOSIX(self.uri)
        uri = self.uri
        #uri = "\\ ".join( p for p in uri.split(" "))
        pipestr = 'filesrc location=' + uri + ' ! \n' + 'oggdemux ! vorbisdec ! audioconvert ! alsasink \n'

        try:
            print "AAAA" #self._player = gst.parse_launch(pipestr)
        except gobject.GError, e:
            logger.info("No es posible crear la tuberia,", str(e))
            return -1

        def eventos(bus, msg):
            t = msg.type
            if t == gst.MESSAGE_EOS: 
                loop.quit()
                
            elif t == gst.MESSAGE_ERROR:
                e, d = msg.parse_error()
                logger.info("ERROR:" + str(e))
                loop.quit()
            
            return True    
    
        player.get_bus().add_watch(eventos)
  
        player.set_state(gst.STATE_PLAYING)
    
        loop = gobject.MainLoop()
        try:
            logger.info("Reproduciendo...")
            self._playing = True
            loop.run()
        except KeyboardInterrupt: # Por si se pulsa Ctrl+C
             pass
    
        self.Stop()

    def Play2(self):
        logger.info("GST Play called")
        if len(self._playlist) <= 0:
            logger.info("Playlist empty")
            return

        if self._current < 0:
            self._current = 0

        if self._playing: self.Stop()

        self._player = gst.element_factory_make ("playbin", "play")
        bus = self._player.get_bus()
	bus.add_watch(self.on_message)

        logger.info("settings uri="+self._playlist[self._current])
        self._player.set_property ("uri", self._playlist[self._current])
        self._player.set_state (gst.STATE_PLAYING)
        self._playing = True

    def Stop(self):
        logger.info("Stop called")
        if not self._playing: return

        logger.info("Stopping..")
        self._player.set_state (gst.STATE_NULL)
        self._playing = False

    def Seek(self, time):
        self.time_format = gst.Format(gst.FORMAT_TIME)
        self._player.seek_simple(self.time_format, gst.SEEK_FLAG_FLUSH, time)
        pass

    def getVolume(self):
        return 1

