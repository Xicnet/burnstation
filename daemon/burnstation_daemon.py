#!/usr/bin/python
#
# mediabase daemon - creates users' homes, imports files and generates thumbnails
# by rama@r23.cc

MODULE = 'daemon'

import SocketServer
import sys, os, os.path
sys.path.append(os.getcwd())
sys.path.append("..")

from LoadConfig import config
from ErrorsHandler import *

#from gst_player import OggPlayer
from mpd_player import OggPlayer

PORT = 4096

#-----------------------------------------------------------------
# server
#-----------------------------------------------------------------

p = OggPlayer()

class TCPRequestHandler(SocketServer.BaseRequestHandler ):
    global p
    #--------------------------------------------------------------------
    def setup(self):
        self.player = p
        #logger.info( str(self.client_address), 'connected!' )
        logger.info( 'Client connected!' )
        welcome = 'OK Welcome to burnstation server.'
        #self.request.send(welcome + ' Hi '+ str(self.client_address) + '!\n')
        #self.request.send('player status: %s\n' % self.player.status)
        self.QUIT = False

    #--------------------------------------------------------------------
    def handle(self):
        while 1:

            data = self.request.recv(10240)
            logger.info( 'OK Got command: ' + data.strip() )

            if data.strip() == 'QUIT':
                logger.info( 'quitting..' )
                return
            else:
                if ( data[:5] == 'PLAY ' ):
                    file = data[5:]
                    #self.request.send("Playing file: %s" % file)
                    try:
                        self.player.AddToPlaylist(file)
                        self.request.close()
                        self.player.Play()
                    except Exception, e: logger.error("burnstation daemon EXCEPTION: " + str(e))
                    #self.request.send('player status: %s\n' % self.player.status)
                    return
                elif ( data[:5] == 'STOP ' ):
                    self.player.Stop()
                    return
                elif ( data[:5] == 'SEEK ' ):
                    position = data[5:]
                    try: self.player.Seek(int(position))
                    except Exception, e: logger.error("burnstation daemon EXCEPTION: " + str(e))
                    #self.request.send('player status: %s\n' % self.player.status)
                    return
                elif ( data[:5] == 'VOLU ' ):
                    level = float(data[5:])
                    try: self.player.SetVolume(level)
                    except Exception, e: logger.error("burnstation daemon EXCEPTION: " + str(e))
                    return
                elif ( data[:5] == 'BURN_' ):
                    try:
                        #mode   = data[5:6]
                        #tracks = data[7:-1].split(':')
                        commands   = data.split("|||")
                        print "COMMANDS : ", commands
                        mode = commands[0].split("_")[1]
                        print "MODE : ", mode
                        tracks = commands[1].split(":")

                        if   mode == 'A': mode = 'AUDIO'
                        elif mode == 'D': mode = 'DATA'
                        elif mode == 'U': mode = 'USB'

                        #logger.debug(mode)
                        #logger.debug(tracks)

                        # FIXME : ugly hardcode
                        home = "/usr/share/burnstation-client-2.0"
                        cmd = home + '/burn.py'
                        args = [cmd, mode]

                        for track in tracks:
                            if track != '':
                                args.append(track)

                        logger.debug("-------------------------------")
                        logger.debug("TRACKS")
                        logger.debug(tracks)
                        logger.debug("-------------------------------")
                        logger.debug(args)
                        logger.debug("-------------------------------")
                        logger.debug(args)
                        logger.debug("-------------------------------")

                        try:
                            logger.debug("Spawning burn script..")
                            b = os.spawnve(os.P_NOWAIT, cmd, args, os.environ)
                        except Exception, e: logger.error("burnstation daemon EXCEPTION: " + str(e))

                        return
                    except Exception, e:
                        logger.error("EXCEPTION: %s" % str(e))
                else:
                    #self.request.send('ERR command not found: %s\n' % data)
                    logger.error('ERR command not found: %s\n' % data)
                    return

    #--------------------------------------------------------------------
    def finish(self):
        #print self.client_address, 'disconnected!'
        logger.info( 'Client ready for disconnection!' )
        try: self.request.send('OK bye ' + str(self.client_address) + '\n')
        except Exception, e: logger.error("burnstation daemon EXCEPTION: " + str(e))
        logger.info( 'Disconnecting' )
        #self.QUIT = True
        return

#--------------------------------------------------------------------
def stop_daemon():
    stop_daemon_cmd = "kill -9 `ps ax | grep python.*burnstation_daemon | grep -v grep | awk '{print $1}'`"
    os.system(stop_daemon_cmd)

#--------------------------------------------------------------------
if __name__ == '__main__':
    print 1
    if len(sys.argv) < 2:
        print "Usage: burnstation_daemon.py [start|stop]"
        sys.exit(0)
    if sys.argv[1] == 'stop':
            # stop the daemon
            stop_daemon()
            sys.exit(0)
    print 2
    try:
        pid = os.fork()
        print "start"
        if pid > 0:
            print "daemon PID is: " + str(pid)
            sys.exit(0)
    except OSError, e:
        print >>sys.stderr, "fork failed: %d (%s)" % (e.errno, e.strerror)
        sys.exit(1)

    try:
        # server host is a tuple ('host', PORT)
        tcpserver = SocketServer.ThreadingTCPServer(('127.0.0.1', PORT), TCPRequestHandler)
        tcpserver.allow_reuse_address = True
        tcpserver.serve_forever()
    except Exception, e:
        logger.error(MODULE+" EXCEPTION: " + str(e))
        logger.error(MODULE+" NOT starting")
"""

if __name__ == '__main__':
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        print >>sys.stderr, "fork failed: %d (%s)" % (e.errno, e.strerror)
        sys.exit(1)
    tcpserver = SocketServer.ThreadingTCPServer(('127.0.0.1', PORT), TCPRequestHandler)
    tcpserver.allow_reuse_address = True

    tcpserver.serve_forever()

"""
