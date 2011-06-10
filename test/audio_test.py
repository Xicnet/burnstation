import gst_player
import time

o = gst_player.OggPlayer()

uri = "http://82.94.213.7/dfm_1"

o.AddToPlaylist(uri)

o.Play0(uri)
time.sleep(10)
o.Stop()
