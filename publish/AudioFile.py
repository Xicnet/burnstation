#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os.path
sys.path.append('..')
sys.path.append('../lib')
from ErrorsHandler import *
import MySQLdb

class AudioFile:
    def __init__(self, fn=None, mode='publish'):
        self.SetFile(fn)
        self.mode = mode

    def SetFile(self, fn):
        self.fn = fn
	self.filename = os.path.basename(fn)

        name, ext  = os.path.splitext(self.filename)

        if ext == '.ogg' or ext == '.OGG':
            from VorbisFile import VorbisFile

            self.af = VorbisFile(fn)

        elif ext == '.mp3' or ext == '.MP3':
            from MP3File import MP3File
            self.af = MP3File(fn)

    def read_comments(self):
        return self.af.read_comments()

    def write_comments(self, metadata, userInfo, cache=1, removeSpool=0):
        '''
        Write comments to file. We cache it by default assuming an OGG file.
	If writing comments to a recently converted MP3 file, we do not cache it
	because the MP3-to-OGG conversion drops it already on the cache (spool) dir,
	so we use that one.
        '''

        # do not cache to spool the file being tagged if we are in edit mode.
	# write directly the file in the user's home instead.
        if self.mode is 'edit': cache = 0

        return self.af.write_comments(metadata, userInfo, cache, removeSpool)

    def getFilepath(self):
        return self.fn

    def getFilename(self):
        return self.filename

    def getTag(self, tag):
        return self.af.getTag(tag)

    def getLength(self):
        return self.af.getLength()

    def getBitrate(self):
        return self.af.getBitrate()

    def getSamplerate(self):
        return self.af.getSamplerate()

    def getInfo(self):
	'''Available info (for OGG/Vorbis) is:  channels, bitrate, serial, sample_rate, length'''
        return self.af.info()

    def listTags(self):
        return self.af.listTags()

    def getSize(self):
        return os.stat(self.fn).st_size
