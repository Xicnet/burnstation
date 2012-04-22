#!/bin/env python
# -*- coding: utf-8 -*-

from LoadConfig import config
import MySQLdb
from ErrorsHandler import *

class DB:
    def __init__(self):
        logger.info("instantiated DB class")

    def connect(self):
        db = MySQLdb.connect(host=config.DBhost, user=config.DBuser, passwd=config.DBpass, db=config.DB)
        if not hasattr(db, 'set_character_set'):
            print "NO"
            #db.character_set_name('utf8')
        else:
            db.set_character_set('utf8')

        return db
