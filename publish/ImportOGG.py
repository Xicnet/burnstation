#!/usr/bin/python
# -*- coding: utf-8 -*-

import  sys
sys.path.append('..')
from ErrorsHandler import *
import  LoadConfig
from ImportCommon import *
import  MySQLdb
import re
import os.path

from AudioFile import AudioFile
from MiscTools import *

from DB import DB
DB = DB()

from User import User
user = User()

#---------------------------------------------------------------------------

class ImportOGG:
    def __init__(self, fn, userInfo, mode='publish'):
	self.fn             = fn
	self.userInfo       = userInfo
	self.mode           = mode
        self.warnIncomplete = 1
	tags                = ''

        self.config        = LoadConfig.LoadConfig()

	# open ogg file
	self.af           = AudioFile(fn)
	self.metadata     = self.af.read_comments()

        if self.mode is 'publish':
            #newFilePath = self.MoveImported(self.fn, self.userInfo['home'], self.userInfo['spoolDir'])
            #newFilePath = removePathComponent(self.fn, "/usr/local/media/")
            newFilePath = self.fn
            #print newFilePath
            logger.debug5( "ImportOGG() self.fn: " + self.fn )
            logger.debug5( "ImportOGG() newFilePath: " + newFilePath )

            if newFilePath:
                if self.import2db(newFilePath):
                    self.setImported()
        elif self.mode is 'edit':
            if self.import2db(self.fn):
                logger.debug1( "Updated database from file: %s" % self.fn )
	
    def isImported(self, path):
        # replace .mp3 with .ogg to search on the database, as we do not have .mp3s there
        #metadata = {"title":"TTTIIITTTLLLEEE", "artist":"AAARRRTTTIIISSSTTT", "license":"LLLIIICCCEEENNNSSSEEE"}
        metadata = {}

        path = removePathComponent(self.fn, "/usr/local/media/")
        name, ext = os.path.splitext(path)

        path = name + ".ogg"
    
        db = DB.connect()
        cursor = db.cursor()
        sql  = "SELECT tr.id, tr.name, ar.name, al.name, la.name, li.name"
        sql += " FROM netjuke_tracks tr, netjuke_artists ar, netjuke_albums al, netjuke_labels la, licenses li"
        sql += " WHERE location = '%s'" % MySQLdb.escape_string(path)
        sql += " AND tr.ar_id=ar.id AND tr.al_id=al.id AND tr.la_id=la.id AND tr.license=li.id"

	logger.debug99( "Using SQL query to check if file is imported: %s" % sql )
        cursor.execute(sql)
        result = cursor.fetchall()
	record = None
	for record in result:
            metadata['ID']      = record[0]
            metadata['title']   = record[1]
            metadata['artist']  = unicode(record[2], 'utf8')
            metadata['album']   = unicode(record[3], 'utf8')
            metadata['label']   = unicode(record[4], 'utf8')
            metadata['license'] = record[5]

        logger.debug5( "Import.isImported(%s) rowcount = %i" % (path, cursor.rowcount) )

        return (cursor.rowcount, metadata)

    def setImported(self):
        '''
	Should flag or delete from mp3tmp when file was imported, and delete the source file.
	'''

	sourceFile = removePathComponent(self.fn, self.userInfo['spoolDir'])
        name, ext  = os.path.splitext(sourceFile)
        sourceFile = name + ".mp3"

        db = DB.connect()

        sql = "SELECT location FROM mp3tmp WHERE location LIKE '%s'" % MySQLdb.escape_string(sourceFile)
        cursor = db.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
	for record in result:
            sql = "UPDATE mp3tmp SET imported = 1 WHERE location = '%s'" % MySQLdb.escape_string(record[0])
            db.set_character_set('utf8')
            cursor = db.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()

    def MoveImported(self, file, target, spoolDir):
        return moveExactTree(file, target, spoolDir, 1)
    
    def CopyImported(self, file, target, spoolDir):
	logger.debug5( "---------------------------" )
        logger.debug5( "in ImportOGG.CopyImported: " )
        logger.debug5( "file: " + file )
        logger.debug5( "target: " + target )
	logger.debug5( "---------------------------" )

        target = copyExactTree(file, target, spoolDir, 1)

        return target

    def import2db(self, newFilePath):

	self.af.SetFile(newFilePath)
	self.metadata = self.af.read_comments()
        print self.metadata

	location = location2db(newFilePath, self.userInfo['home'])

        if self.mode is 'publish': (isImported, metadata) = self.isImported(location)
        elif self.mode is 'edit': isImported = 1

        logger.debug99( "------------------------------------" )
        logger.debug99( "in ImportOGG.import2db():" )
	logger.debug99( "user home   = " + self.userInfo['home'] )
        logger.debug99( "is imported = " + str(isImported) )
        logger.debug99( "newFilePath = " + newFilePath )
        logger.debug99( "location    = " + location )
        logger.debug99( "------------------------------------" )
        
	if (self.mode is 'publish') and isImported:
            logger.debug1( "File already imported.. skipping: %s" % location )
            return

        artistID = getID('artists', self.metadata['artist'])
        albumID = getID('albums', self.metadata['album'])
        labelID = getID('labels', self.metadata['label'])
        licenseID = getID('licenses', self.metadata['license'])

        if artistID == 1 or albumID == 1 or labelID == 1 or licenseID == 1:
            logger.warn("Incomplete tags for file!")
            self.warnIncomplete = 0

        filename = os.path.basename(newFilePath)

        if self.metadata['title'] == '': title = MySQLdb.escape_string(filename)
        else: title = MySQLdb.escape_string(uniconvert2(self.metadata['title']).encode('utf8'))
        size = self.af.getSize()
	time = int( self.af.getLength() )
	track_number = self.af.getTag('track_number')
	if track_number == '': track_number = self.af.getTag('tracknumber')
	if track_number == '': track_number = 0
	year = self.af.getTag('year')
	if year == '': year = 0
	bitrate = self.af.getBitrate()
	sample_rate = self.af.getSamplerate()
	kind = 'OGG/Vorbis'
	location = MySQLdb.escape_string(uniconvert2(location).encode('utf8'))
	comments = MySQLdb.escape_string(uniconvert2(self.metadata['comment']).encode('utf8'))

        if self.mode is 'publish':
            sql = "INSERT INTO"
        elif self.mode is 'edit':
            sql = "UPDATE"
            trackID = getIDbyLocation(location)

        sql += " netjuke_tracks SET ar_id = '"+ str(artistID) +"', al_id = '"+ str(albumID) +"', ge_id = '1', la_id = '"+ str(labelID) +"', name = '"+ title +"', size = '"+ str(size) +"', time = '"+ str(time) +"', track_number = '"+ str(track_number) +"', year = '"+ str(year) +"', date = now(), bit_rate = '"+ str(bitrate) +"', sample_rate = '"+ str(sample_rate) +"', kind = '"+ kind +"', location = '"+ str(location) +"', comments = '"+ comments +"', mtime = now(), license = '"+ str(licenseID) +"', lg_id = '1', enabled = 2"

        if self.mode is 'edit': sql += " WHERE id = %s" % str(trackID)

        logger.debug99( "Using SQL query: " + sql )

        db = DB.connect()
        cursor = db.cursor()
        cursor.execute(sql)

        fileID = db.insert_id()
        self.DoFileUploaderRelation(fileID, self.userInfo['ID'])

	# FIXME: do some checks, and return False if this fails
	return True

    def DoFileUploaderRelation(self, fileID, userID):
        sql = "INSERT IGNORE INTO file_uploader SET file = '%i', uploader = '%i'" % (fileID, userID)
        logger.debug99( "Using SQL query: " + sql )

        db = DB.connect()
        cursor = db.cursor()
        cursor.execute(sql)

#---------------------------------------------------------------------------
if __name__ == '__main__':
    if len(sys.argv) > 1:
        oggFile   = sys.argv[1]
        userEmail = sys.argv[2]

        userInfo = user.GetInfo(userEmail)

        # Uncomment the following line for tests
        ImportOGG(oggFile, userInfo)

