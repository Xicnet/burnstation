#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, string, MySQLdb, getopt, os.path
sys.path.append('..')
sys.path.append('../import')
sys.path.append('../lib')

from LoadConfig import config
from ErrorsHandler import *

db = MySQLdb.connect(host=config.DBhost, user=config.DBuser, passwd=config.DBpass, db=config.DB)
from RecursiveParser import RecursiveParser
from mutagen.oggvorbis import OggVorbis
import time

from ImportOGG import ImportOGG
from MiscTools import *

from User import User
user = User()

class Publisher:
    def __init__(self, source, label=None):
        self.source      = source
        self.label    = label
        self.userInfo = user.GetInfo("admin@burnstation.org")
        self.files    = self.getFiles()

    #---------------------------------------------------
    def getFiles(self):
        """
        If source is a dir, scan it recursively and return all files.
        Otherwise, source is just that file.
        """

        source = []

        if os.path.isfile(self.source):
            source.append(self.source)
        elif os.path.isdir(self.source):
            try:
                parser = RecursiveParser()
                supportedFormats = ['ogg']

                source = parser.getRecursiveFileList(self.source, supportedFormats)
            except Exception, e: logger.error( "ERROR. There was an exception: %s" % str(e) )
        return source

    #---------------------------------------------------
    def saveLabel(self, file, label):
        '''read file and save label tag'''
        af = OggVorbis(file)

        logger.info( "Tags BEFORE labelizer: " + str(af) )

        af['label'] = label
        af.save()
        logger.info( "Tags AFTER labelizer: " + str(af) )

    #---------------------------------------------------
    def label_tagger(self):
        "Recursively tag files with their proper 'Label' tag (metadata)..."

        if self.label is not None:
            for file in self.files: self.saveLabel(file, self.label)

    #---------------------------------------------------
    def import2db(self):
        "Recursively import files from directory specified during instantiation"

        target = self.userInfo['home']
        for file in self.files:
            print "*+"*77
            print "import2db src   : ", file
            print "import2db target: ", target
            print "++"*77
            newFile = copyExactTree(file, target, config.import_basedir, 1)
            ImportOGG(newFile, self.userInfo)


#---------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) > 2:
        basedir = sys.argv[1] # TODO check if the directory exists and quit with warning if not
        label   = sys.argv[2]

        publisher = Publisher(basedir, label)
        publisher.label_tagger()
        publisher.import2db()
    else:
        logger.error( "[!!] ERROR: You MUST specify a start directory, and the label name!" )

