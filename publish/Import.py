#!/bin/env python
# -*- coding: utf-8 -*-

import  sys
sys.path.append('..')
from ErrorsHandler import *
import  LoadConfig
from ImportCommon import *

import os
import os.path
import shutil

import  MySQLdb

from ImportOGG import ImportOGG
from RecursiveParser import RecursiveParser
from AudioFile import *
from MP3File import *
from MiscTools import *

import myconvert2ogg

import Msg

from DB import DB
DB = DB()

class Import:
    def __init__(self, userInfo):

        self.config = LoadConfig.LoadConfig()
        self.userInfo = userInfo

    def Process(self, dir, status):
        self.dir = dir
        self.status = status

        # first process dir to copy OGG files to spoolDir and convert MP3 files to spoolDir
        self.ProcessDir(dir)

	# if there are MP3 files, they must be converted to OGG into the spoolDir
	# before they can be imported
        #self.convert2ogg()

	# finally import all OGG files from the spoolDir
        self.ImportOggFiles()

    def ProcessDir(self, dir):
        logger.debug3( "on Import.ProcessDir(): should process basedir: %s ..." % dir )
        dirlist = os.listdir(dir)

        for x in dirlist:
            name, ext  = os.path.splitext(x)

            if x != get_ascii_filename(x):
                continue

            if ext.lower() == '.ogg' or ext.lower() == '.mp3':
                file = dir +'/'+ x

		logger.debug3( "found file: %s ... with ext=%s" % (file, ext) )

                # if we hit an MP3 file we convert to OGG into the spoolDir
                # using cached metadata if we have it
                if ext.lower() == '.mp3': self.convert2ogg(file)
                if ext.lower() == '.ogg': self.copy2spool(file)
    
    def ImportOggFiles(self):
	parser = RecursiveParser()

        #supportedFormats = ['ogg', 'mp3', 'wav']
        supportedFormats = ['ogg']

        files = parser.getRecursiveFileList(self.userInfo['spoolDir'], supportedFormats)
        
	for x in files:
            status = "Importing: %s ..." % os.path.basename(x)
            logger.debug1(status)
            self.status.SetLabel(status)
            ImportOGG(self, x, self.userInfo)

        status = "*** !! Import finished !! ***"
        logger.debug1(status)
        self.status.SetLabel(status)
	Msg.Msg('Publish', 'Import Finished !!', 'Imp', 330, 210, 0)

    def convert2ogg(self, file):
        '''
        Get list of tagged files by user, convert them to OGG, and place the tags.
        '''
        logger.debug2( "Starting OGG conversion of MP3 file: %s" % file )

	mp3file    = MP3File()
	mp3file.SetFile(file)
        metadata = mp3file.read_comments(self.userInfo)

        i = 0
	location = ''
        #for file in files:
	if True:
            location = file
            filename = os.path.basename(location)

	    tmpDir = self.config.spoolPath + self.userInfo['nickname']
            newBaseDir = tmpDir + os.path.dirname(location)

	    name, ext  = os.path.splitext(location)
            outfile = tmpDir + name + ".ogg"

            if not os.path.exists(newBaseDir):
                logger.debug3( "Creating: %s before OGG conversion" % newBaseDir )
                os.makedirs(newBaseDir)

            self.status.SetLabel("Converting to OGG: %s ..." % filename)

            logger.info( "location: %s / outfile: %s" % (QuoteForPOSIX(location), QuoteForPOSIX(outfile)) )
            myconvert2ogg.main(location, outfile)
	    #logger.debug3( "Running conversion command : " + cmd )

            #cmd = "cd ./import ; ./my_dir2ogg %s -o %s" % (QuoteForPOSIX(location), QuoteForPOSIX(outfile))
	    #logger.debug3( "Running conversion command : " + cmd )
            #os.system(cmd)

            logger.debug5("Will now write tags to OGG files converted from MP3")
	    #logger.debug5( metadata )
            af = AudioFile(outfile)

	    af.write_comments(metadata, self.userInfo, 0, 1)
	    i = i + 1

    def copy2spool(self, file):
        logger.debug3( ".......about to copy: %s to spooldir: %s" % (file, self.userInfo['spoolDir']) )
        copyExactTree(file, self.userInfo['spoolDir'], self.userInfo['nickname'], 0)

    def isImported(self, path):
        # replace .mp3 with .ogg to search on the database, as we do not have .mp3s there
        #metadata = {"title":"TTTIIITTTLLLEEE", "artist":"AAARRRTTTIIISSSTTT", "license":"LLLIIICCCEEENNNSSSEEE"}
        metadata = {}

        path = removePathComponent(path, self.userInfo['home'] )
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

    def isCached(self, sourcePath):
        '''check if file is cached in the spoolDir and return it if true, otherwise return the given source'''

        inCache = self.userInfo['spoolDir']+sourcePath

        if os.path.isfile(inCache): return inCache
        else: return sourcePath
    
    def CleanCache(self):
        logger.debug1( "Cleaning cache for %s user..." % self.userInfo['nickname'] )
        if os.path.isdir(self.userInfo['spoolDir']):
            try:
                shutil.rmtree(self.userInfo['spoolDir'])
                logger.debug1( "Cache is clean now!" )

            except Exception, e: logger.debug1( "ERROR trying to remove user's spoolDir: %s, got: %s" % (self.userInfo['spoolDir'],e) )

        db = DB.connect()
        cursor = db.cursor()
        sql = "DELETE FROM mp3tmp WHERE uploader = '%i'" % self.userInfo['ID']
	logger.debug99( "Using SQL query to remove last import rubbish: %s" % sql )
        cursor.execute(sql)

    def Unimport(self, file):
        db = DB.connect()

        location = self.userInfo['nickname'] + os.path.splitext(str(file))[0] + ".ogg"
        location = removePathComponent(location, self.userInfo['home'])
        logger.info("! Unimporting ! : " + location)

        fileID = getIDbyLocation(location)
        logger.info("with ID !!: " + str(fileID))

        sql = "DELETE FROM netjuke_tracks WHERE id = '%i'" % fileID
	logger.debug99( "Using SQL query to Unimport fileID = %i : %s" % (fileID, sql))
        cursor = db.cursor()
        cursor.execute(sql)

        sql = "DELETE FROM file_uploader WHERE file = '%i'" % fileID
	logger.debug99( "Using SQL query to Unimport fileID = %i : %s" % (fileID, sql))
        cursor = db.cursor()
        cursor.execute(sql)

        logger.debug("unlink(file) = %s" % self.config.musicPath + location)
        try: os.unlink(self.config.musicPath + location)
        except Exception, e: logger.debug1( "ERROR: on Unimport() trying to unlink file, got: " + str(e) )

