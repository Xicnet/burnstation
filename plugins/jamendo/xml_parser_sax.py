#!/usr/bin/python

from xml.sax import make_parser
from xml.sax.handler import ContentHandler 

"""
<Tracks>
      <track lengths="11166" albumID="2970" trackno="1" id="21242">
               <dispname>11adasd1Lodasro</dispname>
               <lyrics>11dasds]</lyrics>
      </track>

      <track lengths="66" albumID="2971" trackno="1" id="2122">
               <dispname>LosEnatschos-intro</dispname>
               <lyrics>sadsad</lyrics>
      </track>

</Tracks>
""" 

track_list = []

class TracksHandler(ContentHandler):

    def __init__ ( self ):
        self.d = {}
        self.lengths = False
        self.albumID = False
        self.trackno = False
        self.dispname = False
        self.lyrics = False
        self.track = False        

    def startElement(self, name, attrs):
        if name == "dispname":
            self.dispname = True 
        elif name == "lyrics":
            self.lyrics = True
        elif name == 'track':
            self.track = True      
            self.lengths = attrs.get('lengths',"")
            self.albumID = attrs.get('albumID',"")
            self.trackno = attrs.get('trackno',"")

    def endElement(self, name):
        if name == 'track':
            track_list.append ( self.d )
            self.d = {}
        elif name == 'dispname':
            self.dispname = False
        elif name == 'lyrics':
            self.lyrics = False

    def characters (self, content):
        if self.dispname: self.d['dispname'] = content
        elif self.lyrics: self.d['lyrics'] = content

        if self.track:
            self.d['track_length'] = self.lengths
            self.d['track_albumID'] = self.albumID
            self.d['track_trackno'] =self.trackno


parser = make_parser()    
parser.setContentHandler(TracksHandler())
parser.parse("bla2.xml") #change this
#parser.parse("/tmp/jamendo_dump")   

for track in track_list:
    print track
