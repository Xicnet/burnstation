#!/usr/bin/python
#
# mediabase daemon - creates users' homes, imports files and generates thumbnails
# by rama@r23.cc

import SocketServer
import sys, os
sys.path.append("..")

import LoadConfig
config = LoadConfig.LoadConfig()

import gst_player

PORT = 4096
#PORT = 4097

#-----------------------------------------------------------------
# server
#-----------------------------------------------------------------
class player:
    def __init__(self):
        self.status = "stopped"

    def play(self):
        self.status = "playing"

    def stop(self):
        self.status = "stopped"

#p = player()

p = gst_player.OggPlayer()

class TCPRequestHandler(SocketServer.BaseRequestHandler ):
    global p
    def setup(self):
        self.player = p
        print self.client_address, 'connected!'
        welcome = 'OK Welcome to burnstation server.'
        #self.request.send(welcome + ' Hi '+ str(self.client_address) + '!\n')
        #self.request.send('player status: %s\n' % self.player.status)
        self.QUIT = False

    def handle(self):
        while 1:
            if self.QUIT: self.request.close()

            data = self.request.recv(1024)
            print 'OK Got command: ' + data.strip()

            if data.strip() == 'CLOSE':
                return
            if data.strip() == 'QUIT':
                sys.exit(0)
            else: 
                if ( data[:5] == 'PLAY ' ):
                    file = data[5:].split(':')
                    #self.request.send("Playing file: %s" % file)
                    try:
                        self.player.AddToPlaylist(file[0])
                        self.request.close()
                        self.player.Play()
                    except Exception, e: logger.error("burnstation daemon EXCEPTION: " + str(e))
                    #self.request.send('player status: %s\n' % self.player.status)
                elif ( data[:5] == 'STOP ' ):
                    self.player.Stop()
                elif ( data[:5] == 'SEEK ' ):
                    position = data[5:]
                    try: self.player.Seek(int(position))
                    except Exception, e: logger.error("burnstation daemon EXCEPTION: " + str(e))
                    #self.request.send('player status: %s\n' % self.player.status)
                elif ( data[:5] == 'BURN ' ):
                    tracks = data[5:-1].split(':')
                    #self.request.send('starting to burn!\n')
                    cmd = '../scripts/burn'
                    #args = [cmd, '-A', '-a', "/usr/local/media/music/Costellam/cll003_electroputas_electroputas/[cll003]_03_electroputas__De_La_Isla.ogg", "/usr/local/media/music/Costellam/cll003_electroputas_electroputas/[cll003]_04_electroputas__Jimmy.ogg", "/usr/local/media/music/Costellam/cll003_electroputas_electroputas/[cll003]_02_electroputas__Fiebre.ogg", "/usr/local/media/music/Costellam/cll003_electroputas_electroputas/[cll003]_06_electroputas__Ella.ogg", "/usr/local/media/music/Costellam/cll003_electroputas_electroputas/[cll003]_05_electroputas__Veneno.ogg", '-s'] #> /tmp/burn.out 2> /tmp/burn.err'
                    args = [cmd, '-A', '-a']
                    #args.append("/usr/local/media/music/Costellam/cll003_electroputas_electroputas/[cll003]_05_electroputas__Veneno.ogg")
                    for track in tracks:
                        args.append(track)
                    #args.append('-s')

                    #os.system(cmd)
                    b = os.spawnvpe(os.P_NOWAIT, cmd, args, os.environ)

                elif ( data[:7] == 'IMPORT ' ):
                    pass
                else: self.request.send('ERR command not found: %s\n' % data)

    def finish(self):
        print self.client_address, 'disconnected!'
        self.request.send('OK bye ' + str(self.client_address) + '\n')
        self.QUIT = True

#server host is a tuple ('host', PORT)
#server = SocketServer.ThreadingTCPServer(('127.0.0.1', PORT), TCPRequestHandler)
#server.serve_forever()

if __name__ == '__main__':
	try: 
		pid = os.fork() 
		if pid > 0:
			sys.exit(0) 
	except OSError, e: 
		print >>sys.stderr, "fork failed: %d (%s)" % (e.errno, e.strerror) 
		sys.exit(1)
        
	tcpserver = SocketServer.ThreadingTCPServer(('127.0.0.1', PORT), TCPRequestHandler)
	tcpserver.serve_forever()
