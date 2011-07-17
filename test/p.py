import pygst
pygst.require('0.10')
import gst
import gobject, sys

class player:
    def __init__(self):
        gobject.threads_init()
        self.mainloop = gobject.MainLoop()
        self.player = gst.element_factory_make("playbin", "player")

        self.mainloop.run()

    def play_uri(uri):
        " play an uri like file:///home/foo/bar.mp3 "
    
        print 'Playing:', uri
        self.player.set_property('uri', uri)
        self.player.set_state(gst.STATE_PLAYING)
    


uri = "file:///tmp/a.ogg"

p = player()
p.play_uri(uri)
print 1111111
