import xml.parsers.expat

class XML_parser:

    def __init__(self, data):
        # data to be parsed
        self.data = data
        # init parsed list to be returned
        self.list = []
        # current element name
        self.current_element = None

    def start_element(self, name, attrs):
        print 'Start element:', name, attrs
        if name == 'track':
            self.current_element = name
            print "\n" + "STA:"*30 + "\n"
            self.list.append(attrs)
 
    def end_element(self, name):
        print 'End element:', name
        if name == 'track':
            self.current_element = None
            print "\n" + "END:"*30 + "\n"
 
    def char_data(self, data):
        print 'Character data:', repr(data)
        if self.current_element == "track":
            self.list.append(data)
 
    def Parse(self):
        p = xml.parsers.expat.ParserCreate()
        p.StartElementHandler = self.start_element
        p.EndElementHandler = self.end_element
        p.CharacterDataHandler = self.char_data
        #p.Parse(open("/tmp/jamendo_dump").read())
        result = p.Parse(self.data)
        return result


data = """
<Tracks>
      <track lengths="11166" albumID="2970" trackno="1" link="http://www.jamendo.com/track/21242/" licenseURL="http://creativecommons.org/licenses/by-nd/2.0/de/" id="21242">
               <dispname>111LosEnatschos-intro</dispname>
               <lyrics>111[...]</lyrics>
      </track>
 
      <track lengths="66" albumID="2970" trackno="1" link="http://www.jamendo.com/track/21242/" licenseURL="http://creativecommons.org/licenses/by-nd/2.0/de/" id="21242">
               <dispname>LosEnatschos-intro</dispname>
               <lyrics>[...]</lyrics>
      </track>
 
</Tracks>
"""

p = XML_parser(data)
p.Parse()

print
print p.list
