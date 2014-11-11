#!/usr/bin/env python
# 
# Copyright (c) 2002 Vivake Gupta (vivakeATomniscia.org).  All rights reserved.
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA
#
# This software is maintained by Vivake (vivakeATomniscia.org) and is available at:
#     http://www.omniscia.org/~vivake/python/MP3Info.py

import struct
import string

def _from_synch_safe(synchsafe):
    if isinstance(synchsafe, type(1)):
        (b3, b2, b1, b0) = struct.unpack('!4b', struct.pack('!1i', synchsafe))
    else:
        while len(synchsafe) < 4:
            synchsafe = (0,) + synchsafe
        (b3, b2, b1, b0) = synchsafe

    x = 256
    return (((b3 * x + b2) * x + b1) * x + b0)

def _strip_zero(s):
    start = 0
    while start < len(s) and (s[start] == '\0' or s[start] == ' '):
        start = start + 1

    end = len(s) - 1
    while end >= 0 and (s[end] == '\0' or s[end] == ' '):
        end = end - 1

    return s[start:end+1]

class ID3v2Frame:
    def __init__(self, file, version):
        self.name = ""
        self.version = 0
        self.padding = 0
        self.size = 0
        self.data = ""

        self.flags = {}
        self.f_tag_alter_preservation = 0
        self.f_file_alter_preservation = 0
        self.f_read_only = 0
        self.f_compression = 0
        self.f_encryption = 0
        self.f_grouping_identity = 0
        self.f_unsynchronization = 0
        self.f_data_length_indicator = 0

        if version == 2:
            nameSize = 3
        else:
            nameSize = 4
        self.name = file.read(nameSize)

        self.version = version

        if self.name == nameSize * '\0':
            self.padding = 1
            return

        if self.name[0] < 'A' or self.name[0] > 'Z':
            self.padding = 1
            return

        size = ()
        if version == 2:
            size = struct.unpack('!3b', file.read(3))
        elif version == 3 or version == 4:
            size = struct.unpack('!4b', file.read(4))

        if version == 3:  # abc00000 def00000
            (flags,) = struct.unpack('!1b', file.read(1))
            self.f_tag_alter_preservation  = flags >> 7 & 1 #a
            self.f_file_alter_preservation = flags >> 6 & 1 #b
            self.f_read_only               = flags >> 5 & 1 #c
            (flags,) = struct.unpack('!1b', file.read(1))
            self.f_compression             = flags >> 7 & 1 #d
            self.f_encryption              = flags >> 6 & 1 #e
            self.f_grouping_identity       = flags >> 5 & 1 #f
        elif version == 4: # 0abc0000 0h00kmnp
            (flags,) = struct.unpack('!1b', file.read(1))
            self.f_tag_alter_preservation  = flags >> 6 & 1 #a
            self.f_file_alter_preservation = flags >> 5 & 1 #b
            self.f_read_only               = flags >> 4 & 1 #c
            (flags,) = struct.unpack('!1b', file.read(1))
            self.f_grouping_identity       = flags >> 6 & 1 #h
            self.f_compression             = flags >> 3 & 1 #k
            self.f_encryption              = flags >> 2 & 1 #m
            self.f_unsynchronization       = flags >> 1 & 1 #n
            self.f_data_length_indicator   = flags >> 0 & 1 #p

        self.size = _from_synch_safe(size)
        self.data = _strip_zero(file.read(self.size))

_genres = [
    "Blues", "Classic Rock", "Country", "Dance", "Disco", "Funk", "Grunge",
    "Hip-Hop", "Jazz", "Metal", "New Age", "Oldies", "Other", "Pop", "R&B",
    "Rap", "Reggae", "Rock", "Techno", "Industrial", "Alternative", "Ska",
    "Death Metal", "Pranks", "Soundtrack", "Euro-Techno", "Ambient", "Trip-Hop",
    "Vocal", "Jazz+Funk", "Fusion", "Trance", "Classical", "Instrumental",
    "Acid", "House", "Game", "Sound Clip", "Gospel", "Noise", "AlternRock",
    "Bass", "Soul", "Punk", "Space", "Meditative", "Instrumental Pop",
    "Instrumental Rock", "Ethnic", "Gothic", "Darkwave", "Techno-industrial",
    "Electronic", "Pop-Folk", "Eurodance", "Dream", "Southern Rock", "Comedy",
    "Cult", "Gangsta", "Top 40", "Christian Rap", "Pop/Funk", "Jungle",
    "Native American", "Cabaret", "New Wave", "Psychadelic", "Rave",
    "Showtunes", "Trailer", "Lo-Fi", "Tribal", "Acid Punk", "Acid Jazz",
    "Polka", "Retro", "Musical", "Rock & Roll", "Hard Rock", "Folk",
    "Folk/Rock", "National Folk", "Swing", "Fast-Fusion", "Bebob", "Latin",
    "Revival", "Celtic", "Bluegrass", "Avantegarde", "Gothic Rock",
    "Progressive Rock", "Psychedelic Rock", "Symphonic Rock", "Slow Rock",
    "Big Band", "Chorus", "Easy Listening", "Acoustic", "Humour", "Speech",
    "Chanson", "Opera", "Chamber Music", "Sonata", "Symphony", "Booty Bass",
    "Primus", "Porn Groove", "Satire", "Slow Jam", "Club", "Tango", "Samba",
    "Folklore", "Ballad", "Power Ballad", "Rythmic Soul", "Freestyle", "Duet",
    "Punk Rock", "Drum Solo", "A capella", "Euro-House", "Dance Hall", "Goa",
    "Drum & Bass", "Club House", "Hardcore", "Terror", "Indie", "BritPop",
    "NegerPunk", "Polsk Punk", "Beat", "Christian Gangsta", "Heavy Metal",
    "Black Metal", "Crossover", "Contemporary C", "Christian Rock", "Merengue",
    "Salsa", "Thrash Metal", "Anime", "JPop", "SynthPop",
]

class ID3v1:
    def __init__(self, file):
        self.valid = 0

        self.tags = { }

        try:
            file.seek(-128, 2)
        except IOError:
            pass

        data = file.read(128)
        if data[0:3] != 'TAG':
            return
        else:
            self.valid = 1

        self.tags['TT2'] = _strip_zero(data[ 3: 33])
        self.tags['TP1'] = _strip_zero(data[33: 63])
        self.tags['TAL'] = _strip_zero(data[63: 93])
        self.tags['TYE'] = _strip_zero(data[93: 97])
        self.tags['COM'] = _strip_zero(data[97:125])

        if data[125] == '\0':
            self.tags['TRK'] = ord(data[126])

        try:
            self.tags['TCO'] = _genres[ord(data[127])]
        except IndexError:
            self.tags['TCO'] = "(%i)" % ord(data[127])
        

class ID3v2:
    def __init__(self, file):
        self.valid = 0

        self.tags = { }

        self.header_size = 0

        self.major_version = 0
        self.minor_version = 0

        self.f_unsynchronization = 0
        self.f_extended_header = 0
        self.f_experimental = 0
        self.f_footer = 0

        self.f_extended_header_zie = 0
        self.f_extended_num_flag_bytes = 0

        self.ef_update = 0
        self.ef_crc = 0
        self.ef_restrictions = 0

        self.crc = 0
        self.restrictions = 0

        self.frames = []
        self.tags = {}
        
        file.seek(0, 0)
        if file.read(3) != "ID3":
            return
        else:
            self.valid = 1

        (self.major_version, self.minor_version) = struct.unpack('!2b', file.read(2))

        # abcd 0000
        (flags,) = struct.unpack('!1b', file.read(1))
        self.f_unsynchronization = flags >> 7 & 1 # a
        self.f_extended_header   = flags >> 6 & 1 # b
        self.f_experimental      = flags >> 5 & 1 # c
        self.f_footer            = flags >> 4 & 1 # d

        self.header_size = _from_synch_safe(struct.unpack('!4b', file.read(4)))

        while 1:
            if file.tell() >= self.header_size:
                break
            frame = ID3v2Frame(file, self.major_version)
            if frame.padding:
                file.seek(self.header_size)
                break

            self.frames = self.frames + [frame]
            self.tags[frame.name] = frame.data

_bitrates = [
    [ # MPEG-2 & 2.5
        [0,32,48,56, 64, 80, 96,112,128,144,160,176,192,224,256,None], # Layer 1
        [0, 8,16,24, 32, 40, 48, 56, 64, 80, 96,112,128,144,160,None], # Layer 2
        [0, 8,16,24, 32, 40, 48, 56, 64, 80, 96,112,128,144,160,None]  # Layer 3
    ],

    [ # MPEG-1
        [0,32,64,96,128,160,192,224,256,288,320,352,384,416,448,None], # Layer 1
        [0,32,48,56, 64, 80, 96,112,128,160,192,224,256,320,384,None], # Layer 2
        [0,32,40,48, 56, 64, 80, 96,112,128,160,192,224,256,320,None]  # Layer 3
    ]
]

_samplerates = [
    [ 11025, 12000,  8000, None], # MPEG-2.5
    [  None,  None,  None, None], # reserved
    [ 22050, 24000, 16000, None], # MPEG-2
    [ 44100, 48000, 32000, None], # MPEG-1
]                                                                                                               
                                                                                                                  
_modes = [ "stereo", "joint stereo", "dual channel", "mono" ]

_mode_extensions = [
    [ "4-31", "8-31", "12-31", "16-31" ],
    [ "4-31", "8-31", "12-31", "16-31" ],
    [     "",   "IS",    "MS", "IS+MS" ]
]

_emphases = [ "none", "50/15 ms", "reserved", "CCIT J.17" ]

_MP3_HEADER_SEEK_LIMIT = 8192

class MPEG:
    def __init__(self, file):
        self.valid = 0

        file.seek(0, 2)
        self.filesize = file.tell()
        file.seek(0, 0)

        self.version = 0
        self.layer = 0
        self.protection = 0
        self.bitrate = 0
        self.samplerate = 0
        self.padding = 0
        self.private = 0
        self.mode = ""
        self.mode_extension = ""
        self.copyright = 0
        self.original = 0
        self.emphasis = ""
        self.length = 0

        offset, header = self._find_header(file)
        if offset == -1 or header is None:
            return

        self._parse_header(header)
        ### offset + framelength will find another header. verify??
        if not self.valid:
            return

        self._parse_xing(file)
        

    def _find_header(self, file):                                                                                 
        file.seek(0, 0)                                                                                           
        amount_read = 0                                                                                           
                                                                                                                  
        # see if we get lucky with the first four bytes                                                           
        amt = 4                                                                                                   
                                                                                                                  
        while amount_read < _MP3_HEADER_SEEK_LIMIT:                                                               
            header = file.read(amt)                                                                               
            if len(header) < amt:                                                                                 
                # awfully short file. just give up.                                                               
                return -1, None                                                                                   
                                                                                                                  
            amount_read = amount_read + len(header)                                                               
                                                                                                                  
            # on the next read, grab a lot more                                                                   
            amt = 500                                                                                             
                                                                                                                  
            # look for the sync byte                                                                              
            offset = string.find(header, chr(255))                                                                
            if offset == -1:                                                                                      
                continue                                                                                          
            ### maybe verify more sync bits in next byte?                                                         
                                                                                                                  
            if offset + 4 > len(header):                                                                          
                more = file.read(4)                                                                               
                if len(more) < 4:                                                                                 
                    # end of file. can't find a header                                                                          
                    return -1, None                                                                                             
                amount_read = amount_read + 4                                                                                   
                header = header + more                                                                                          
            return amount_read - len(header) + offset, header[offset:offset+4]                                                  
                                                                                                                                
        # couldn't find the header                                                                                    
        return -1, None

    def _parse_header(self, header):
        # AAAAAAAA AAABBCCD EEEEFFGH IIJJKLMM
        (bytes,) = struct.unpack('>i', header)
        mpeg_version =    (bytes >> 19) & 3  # BB   00 = MPEG2.5, 01 = res, 10 = MPEG2, 11 = MPEG1  
        layer =           (bytes >> 17) & 3  # CC   00 = res, 01 = Layer 3, 10 = Layer 2, 11 = Layer 1
        protection_bit =  (bytes >> 16) & 1  # D    0 = protected, 1 = not protected
        bitrate =         (bytes >> 12) & 15 # EEEE 0000 = free, 1111 = bad
        samplerate =      (bytes >> 10) & 3  # F    11 = res
        padding_bit =     (bytes >> 9)  & 1  # G    0 = not padded, 1 = padded
        private_bit =     (bytes >> 8)  & 1  # H
        mode =            (bytes >> 6)  & 3  # II   00 = stereo, 01 = joint stereo, 10 = dual channel, 11 = mono
        mode_extension =  (bytes >> 4)  & 3  # JJ
        copyright =       (bytes >> 3)  & 1  # K    00 = not copyrighted, 01 = copyrighted                            
        original =        (bytes >> 2)  & 1  # L    00 = copy, 01 = original                                          
        emphasis =        (bytes >> 0)  & 3  # MM   00 = none, 01 = 50/15 ms, 10 = res, 11 = CCIT J.17                

        if mpeg_version == 0:
            self.version = 2.5
        elif mpeg_version == 2:
            self.version = 2
        elif mpeg_version == 3:
            self.version = 1
        else:
            return

        if layer > 0:
            self.layer = 4 - layer
        else:
            return

        self.protection = protection_bit

        self.bitrate = _bitrates[mpeg_version & 1][self.layer - 1][bitrate]
        self.samplerate = _samplerates[mpeg_version][samplerate]
        
        if self.bitrate is None or self.samplerate is None:
            return

        self.padding = padding_bit
        self.private = private_bit
        self.mode = _modes[mode]
        self.mode_extension = _mode_extensions[self.layer - 1][mode_extension]
        self.copyright = copyright
        self.original = original
        self.emphasis = _emphases[emphasis]

        if self.layer == 1:
            self.framelength = ((  12 * (self.bitrate * 1000.0)/self.samplerate) + padding_bit) * 4
            self.samplesperframe = 384.0
        else:
            self.framelength =  ( 144 * (self.bitrate * 1000.0)/self.samplerate) + padding_bit
            self.samplesperframe = 1152.0
        self.length = int(round((self.filesize / self.framelength) * (self.samplesperframe / self.samplerate)))

        self.valid = 1

    def _parse_xing(self, file):
        """Parse the Xing-specific header.

        For variable-bitrate (VBR) MPEG files, Xing includes a header which
        can be used to approximate the (average) bitrate and the duration
        of the file.
        """
        file.seek(0, 0)
        header = file.read(128)

        i = string.find(header, 'Xing')
        if i > 0:
            (flags,) = struct.unpack('>i', header[i+4:i+8])
            if flags & 3:
                # flags says "frames" and "bytes" are present. use them.
                (frames,) = struct.unpack('>i', header[i+8:i+12])
                (bytes,) = struct.unpack('>i', header[i+12:i+16])

                if self.samplerate:
                    self.length = int(round(frames * self.samplesperframe / self.samplerate))
                    self.bitrate = ((bytes * 8.0 / self.length) / 1000)

class MP3Info:
    def __init__(self, file):
        self.valid = 0

        self.id3 = None
        self.mpeg = None

        id3 = ID3v1(file)
        if id3.valid:
            self.id3 = id3

        id3 = ID3v2(file)
        if id3.valid:
            self.id3 = id3

        self.mpeg = MPEG(file)


        if self.id3 is None:
            return

        for tag in self.id3.tags.keys():
            if tag == 'TT2' or tag == 'TIT2':
                self.title = self.id3.tags[tag]
            elif tag == 'TP1' or tag == 'TPE1':
                self.artist = self.id3.tags[tag]
            elif tag == 'TRK' or tag == 'TRCK':
                self.track = self.id3.tags[tag]
            elif tag == 'TYE' or tag == 'TYER':
                self.year = self.id3.tags[tag]
            elif tag == 'COM' or tag == 'COMM':
                self.comment = self.id3.tags[tag]
            elif tag == 'TCM':
                self.composer = self.id3.tags[tag]
            elif tag == 'TAL' or tag == 'TALB':
                self.album = self.id3.tags[tag]
            elif tag == 'TPA':
                self.disc = self.id3.tags[tag]
            elif tag == 'TCO' or tag == 'TCON':
                self.genre = self.id3.tags[tag]
                if self.genre and self.genre[0] == '(' and self.genre[-1] == ')':
                    try:
                        self.genre = _genres[int(self.genre[1:-1])]
                    except IndexError:
                        self.genre = ""
            elif tag == 'TEN' or tag == 'TENC':
                self.encoder = self.id3.tags[tag]

if __name__ == '__main__':
    import sys
    i = MP3Info(open(sys.argv[1], 'rb'))
    print i.id3.tags
