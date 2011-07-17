import pygst
pygst.require('0.10')
import gst
import gobject, sys

def play_uri(uri):
    " play an uri like file:///home/foo/bar.mp3 "

    mainloop = gobject.MainLoop()
    player = gst.element_factory_make("playbin", "player")
  
    print 'Playing:', uri
    player.set_property('uri', uri)
    player.set_state(gst.STATE_PLAYING)

    mainloop.run()


uri = "file::///tmp/a.ogg"
play_uri(uri)
