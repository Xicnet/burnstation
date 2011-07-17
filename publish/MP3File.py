#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os.path
sys.path.append('..')
sys.path.append('../lib')
from ErrorsHandler import *

import MySQLdb
import LoadConfig
from ImportCommon import *
from MiscTools import *

from ID3 import *

from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

from DB import DB
DB = DB()

class MP3File:
    def __init__(self, fn=None):
        self.config = LoadConfig.LoadConfig()
	self.tagReader = 'mutagen' # can be mutagen or ID3

        if fn is not None:
            self.SetFile(fn)

    def SetFile(self, fn):
        self.fn = fn
        self.filename = os.path.basename(self.fn)

        if self.tagReader == 'mutagen':
            self.initMutagenID3()
        elif self.tagReader == 'ID3':
            self.initID3()

    def initMutagenID3(self):
        try:
            self.af = MP3(self.fn, ID3=EasyID3)
	    logger.debug2( "Using mutagen.EasyID3 to read MP3 ID3 tags" )
        except InvalidTagError, message:
            logger.debug1( "Invalid (mutagen) ID3 tag:", message )
        
    def initID3(self):
        try:
            self.af = ID3(self.fn)
	    logger.debug2( "Using ID3 to read MP3 ID3 tags" )
        except InvalidTagError, message:
            logger.debug1( "Invalid ID3 tag:", message )

    def read_comments(self, userInfo=None):
        '''
        Read tags from MP3 file, or from database if file was tagged and not yet converted/imported.
        '''

        # check if we have them cached on the database first
        metadata = self.getTagsFromDB(userInfo)

        # otherwise read tags from file
        if not metadata:
            metadata = self.getTagsFromFile()

        return metadata

    def getTagsFromDB(self, userInfo):
        logger.debug3( "Checking if file was tag and unimported in database... " + self.fn )
        tagged = getTaggedMP3s(userInfo, self.fn)
        if tagged:
            logger.debug3( "... detected cached tags!" )
            metadata = buildTags(tagged[0][1])
            #logger.debug4( "Metadata for file follows: ")
	    #logger.debug4( metadata )

	    return metadata
        else:
            logger.debug3( "... not found " )
            return False

    def getTagsFromFile(self):
        if self.tagReader == 'mutagen':
            return self.getTagsMutagen()
        elif self.tagReader == 'ID3':
            return self.getTagsID3()

    def getTagsMutagen(self):
        dic = {'title'       : '',
               'artist'      : '',
               'album'       : '',
               'genre'       : '',
               'date'        : '',
               'tracknumber' : '',
               'comment'     : '',
               'composer'    : '',
               'license'     : '',
               'label'       : ''
              }
	for tag in self.af.keys():
	    tag = tag.lower()
            val = self.af.get(tag).pop(0)
            if (val <> '') and (val.upper() <> 'N/A'): dic[tag] = val

        return dic

    def getTagsID3(self):
        dic = {'title' : '',
               'artist' : '',
               'album' : '',
               'license' : '',
               'label' : '',
               'comment' : ''
              }
	for tag in self.af.keys():
	    tag = tag.lower()
            val = self.af[tag.upper()]
            if val <> '': dic[tag] = val

        return dic

    def cacheTags(self, metadata, userInfo):
        sql = "INSERT INTO mp3tmp SET "
	dic = {}
	i = 0
	for tag in metadata:
	    tag = tag.lower()
            val = metadata[tag]
            if val == "N/A": val = ''
	    if i > 0: sql += ", "
	    if tag == 'date': tag = 'year'

            sql += tag + " = '" + MySQLdb.escape_string(val.encode('utf8')) +"'"
	    i = i + 1
        sql += ", uploader = '"+str(userInfo['ID'])+"'"
        sql += ", location = '"+ MySQLdb.escape_string(self.fn) +"'"

        db = DB.connect()
        cursor = db.cursor()
        logger.debug1( "Caching MP3 metadata in mp3tmp table..." )
	logger.debug4( "Using SQL query: " + sql )
        cursor.execute(sql)
        logger.debug1( ".. Done!" )

    
    def write_comments(self, metadata, userInfo, cache=0, removeSpool=1):
        '''
	For MP3 files, we do not write tags to them.
	We save them temporarily on a mp3tmp table, which is read-out during the import process,
	which will convert those MP3 to OGG/Vorbis and get the tags from that table to write into the vorbis file.
	'''

        logger.debug3( "Checking if already tagged: " + self.fn )
        cachedTags = getTaggedMP3s(userInfo, self.fn)
        if not cachedTags:
            self.cacheTags(self.getTagsFromFile(), userInfo)

        sql = "UPDATE mp3tmp SET "

	dic = {}
	i = 0
	for tag in metadata:
	    tag = tag.lower()
            val = metadata[tag]
            if val == "N/A": val = ''

	    # build up metadata object together with audio file object
            if tag in EasyID3.valid_keys.keys():
                self.af[tag] = val

	    if i > 0: sql += ", "
	    if tag == 'date': tag = 'year'

            sql += tag + " = '" + MySQLdb.escape_string(val.encode('utf8')) +"'"

            logger.debug4( "in write_comments(): " +  tag + " = " + val )
	    i = i + 1

        sql += " WHERE location = '"+ MySQLdb.escape_string(self.fn) +"'"
        sql += " AND uploader = '"+str(userInfo['ID'])+"'"

        db = DB.connect()
        cursor = db.cursor()
        logger.debug1( "Saving MP3 metadata in mp3tmp table..." )
	logger.debug99( "Using SQL query: " + sql )
        cursor.execute(sql)
        logger.debug1( ".. Done!" )

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

