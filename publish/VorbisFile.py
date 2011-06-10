#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os.path
sys.path.append('..')
sys.path.append('../lib')
from ErrorsHandler import *
import  LoadConfig
from ImportCommon import *

import MySQLdb

from mutagen.oggvorbis import OggVorbis
from MiscTools import *

from ImportOGG import ImportOGG

class VorbisFile:
    def __init__(self, fn):
        self.config = LoadConfig.LoadConfig()

        if fn is not None:
            self.SetFile(fn)

    def SetFile(self, fn):
        self.fn = fn
        self.filename = os.path.basename(self.fn)
        self.af = OggVorbis(self.fn)

    def read_comments(self):
        dic = {'title' : '',
               'artist' : '',
               'album' : '',
               'license' : '',
               'label' : '',
               'comment' : ''
              }
	for tag in self.af.keys():
	    tag = tag.lower()
            val = self.af.get(tag).pop(0)
            if val <> '': dic[tag] = val
        return dic

    def write_comments(self, metadata, userInfo, cache=1, removeSpool=0):
        '''
	Cache the file (copy it to a tmp dir) and write the tags there.
        '''

        logger.debug99("called VorbisFile.write_comments()")

        # now write the comments to file (self.af)
	dic = {}
	for tag in metadata:
	    tag = tag.lower()
            val = metadata[tag]

	    # build up metadata object together with audio file object
            if val != '':
                self.af[tag] = val
            else:
                logger.debug3("Not writing tag: %s (was left empty)" % tag)

	self.af.save()
        logger.debug3( "in VorbisFile.write_comments() Done! Wrote tags successfully to %s!" % self.fn )

        # FIXME : el ImportOGG en modo 'edit' es para que re-lea tags y actualice la DB
	#         pero no deberia ir dentro de la clase VorbisFile
        '''
        if not cache:
            logger.debug2("Should re-import/update: %s" % self.fn)
            ImportOGG(self, self.fn, userInfo, 'edit')
        '''
	return self.fn

    def getFilepath(self):
        return self.fn

    def getFilename(self):
        return self.filename

    def getTag(self, tag):
        if self.af.has_key(tag) and self.af[tag] is not '':
            return self.af.get(tag).pop(0)
        else: return ''

    def getLength(self):
        return self.af.info.length

    def getBitrate(self):
        return self.af.info.bitrate

    def getSamplerate(self):
        return self.af.info.sample_rate

    def getInfo(self):
	'''Available info (for OGG/Vorbis) is:  channels, bitrate, serial, sample_rate, length'''
        return self.af.info

    def listTags(self):
        return self.af.keys()

    def getSize(self):
        return os.stat(self.fn).st_size
