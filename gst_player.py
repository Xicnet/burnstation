#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib  
import pygst  
pygst.require("0.10")
import sys, gst, gobject
import gtk
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
        self.volume_level = 0.5

        self._player = gst.element_factory_make("playbin2", "player")

        volume = gst.element_factory_make("volume")
        self._player.add(volume)
        self._player.set_property("volume", self.volume_level)

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
            logger.error("Error: %s . %s" % (err, debug))
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

    def Play(self):
        self.Stop()
        #uri = QuoteForPOSIX(self.uri)
        uri = self.uri
        #uri = "\\ ".join( p for p in uri.split(" "))
        #pipestr = 'filesrc location=' + uri + ' ! \n' + 'oggdemux ! vorbisdec ! audioconvert ! alsasink \n'

        try:
            #self._player = gst.parse_launch(pipestr)

            """
            self._volume = gst.element_factory_make("volume")
            volume = 0.0
            self._volume.set_property("volume", volume)
            """

            logger.info( 'Playing: ' + uri )
            self._player.set_property('uri', uri)
            self._player.set_state(gst.STATE_PLAYING)
        except gobject.GError, e:
            logger.error("No es posible crear la tuberia: " + str(e))
            return -1

        def eventos(bus, msg):
            t = msg.type
            if t == gst.MESSAGE_EOS: 
                loop.quit()
                
            elif t == gst.MESSAGE_ERROR:
                e, d = msg.parse_error()
                logger.error("ERROR:" + str(e))
                loop.quit()
            
            return True    
    
        self._player.get_bus().add_watch(eventos)
    
        self._player.set_state(gst.STATE_PLAYING)
    
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
        if not self._playing: return

        self._player.set_state (gst.STATE_NULL)
        self._playing = False

    def Seek(self, time):
        try:
            self.time_format = gst.Format(gst.FORMAT_TIME)

            pos_int = self._player.query_position(self.time_format, None)[0]
            seek_ns = pos_int + (time * 1000000000)
            self._player.seek_simple(self.time_format, gst.SEEK_FLAG_FLUSH, seek_ns)
            logger.info("gst_player: seeking to position: %i" % pos_int)
        except Exception, e: logger.error("gst_player EXCEPTION: " + str(e))

    def SetVolume(self, level):
        self.volume_level = level
        logger.info("gst_player: setting volume to: %f" % level)
        self._player.set_property("volume", self.volume_level)

