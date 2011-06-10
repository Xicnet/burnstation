#!/usr/bin/python
# -*- coding: utf-8 -*-

import  sys
sys.path.append('..')
from ErrorsHandler import *
import  LoadConfig
config = LoadConfig.LoadConfig()

from DB import DB
DB = DB()

class User:
    def __init__(self):
        pass

    def GetInfo(self, email):
        logger.debug2( "Getting user info..." )
        db = DB.connect()
        cursor = db.cursor()
        sql = "/* GetUserInfo() */ SELECT id, nickname FROM netjuke_users WHERE email = '%s'" % email
        cursor.execute(sql)
        result = cursor.fetchall()

        userInfo = {}

	record = None
	for record in result:
	    userInfo['ID'] = record[0]
	    userInfo['nickname'] = record[1]
	    userInfo['home'] = config.musicPath + userInfo['nickname']
	    userInfo['spoolDir'] = config.spoolPath + userInfo['nickname']
	
	return userInfo
