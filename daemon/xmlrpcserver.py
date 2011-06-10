#!/usr/bin/python
#
# mediabase daemon - creates users' homes, imports files and generates thumbnails
# by rama@r23.cc

MODULE = 'daemon'

import SocketServer, SimpleXMLRPCServer

import sys, os, os.path
sys.path.append(os.getcwd())
sys.path.append("..")

import LoadConfig
config = LoadConfig.LoadConfig()
from ErrorsHandler import *

import gst_player

PORT = 4096

#-----------------------------------------------------------------
# server
#-----------------------------------------------------------------

p = gst_player.OggPlayer()

class MyXMLRPCObject:
    global p
    def __init__(self):
        # Make all of the Python string functions available through
        # python_string.func_name
        import string
        self.python_string = string
        self.player = p
        logger.info( 'Client connected!' )
        welcome = 'OK Welcome to burnstation server.'

    def play(self, file):
        try:
            self.player.AddToPlaylist(file)
            self.player.Play()
        except Exception, e: logger.error("burnstation daemon EXCEPTION: " + str(e))
        #self.request.send('player status: %s\n' % self.player.status)
        return True

    def _privateFunction(self):
        # This function cannot be called through XML-RPC because it
        # starts with an '_'
        pass
    
    def chop_in_half(self, astr):
        return astr[:len(astr)/2]

    def burn_to_usb(self, tracks_list, playlistID):
        print "Burning to USB..."
        print "Tracks list: ", tracks_list
        print "Playlist ID: ", playlistID
        return True

    def repeat(self, astr, times):
        return astr * times


class SimpleThreadedXMLRPCServer(SocketServer.ThreadingMixIn, SimpleXMLRPCServer.SimpleXMLRPCServer):
        pass

"""
if __name__ == "__main__":
        server = SimpleThreadedXMLRPCServer(("localhost",8003))
	server.allow_reuse_address = True
        server.register_instance(MyXMLRPCObject()) # register your distant Object here
        server.serve_forever()
"""

if __name__ == '__main__':
	if sys.argv[1] == 'stop':
            # stop the daemon
            stop_daemon()
            sys.exit(0)

	try: 
		pid = os.fork() 
		if pid > 0:
			print "daemon PID is: " + str(pid)
			sys.exit(pid) 
	except OSError, e: 
		print >>sys.stderr, "fork failed: %d (%s)" % (e.errno, e.strerror) 
		sys.exit(1)
        
	try:
            # server host is a tuple ('host', PORT)
            server = SimpleThreadedXMLRPCServer(("localhost", 8003))
            server.allow_reuse_address = True
            server.register_instance(MyXMLRPCObject()) # register your distant Object here
            server.serve_forever()
        except Exception, e:
            logger.error(MODULE+" EXCEPTION: " + str(e))
            logger.error(MODULE+" daemon NOT starting")

