import xmlrpclib


tracks_list = ['track UNO', 'track DOS']
playlistID  = 129

server = xmlrpclib.Server('http://localhost:8003')
#print server.chop_in_half('I am a confidant guy')


file = "file:///media/usb1000/media/BURNSTATION/music/notype/[NT 075] n.kra - bits.pieces/075-01-n.kra-mangle.ogg"
#print server.burn_to_usb(tracks_list, playlistID)
print "server.play(file) returned: ", server.play(file)
print "HOLA"


#print server.repeat('Repetition is the key to learning!\n', 5)
#print server._string('<= underscore')
#print server.python_string.join(['I', 'like it!'], " don't ")
#print server._privateFunction() # Will throw an exception

