import time
import sys
sys.path.append("..")

import gst_player

o = gst_player.OggPlayer()

uri = "/tmp/a.ogg"
o.AddToPlaylist(uri)

o.Play()
o.Stop()
