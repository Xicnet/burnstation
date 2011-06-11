#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb
import  sys
from os.path import isfile
from os import rename
from shutil import copy
sys.path.append('..')
import  LoadConfig
config = LoadConfig.LoadConfig()

import urllib
from MiscTools import *

db = MySQLdb.connect(host=config.DBhost, user=config.DBuser, passwd=config.DBpass, db=config.DB)
db.set_character_set('utf8')

#--------------------------------------------------------------------
def get_whitespace_tracks():
    sql = "SELECT id, location FROM netjuke_tracks WHERE location REGEXP '.* .*' LIMIT 100"
    #logger.debug( sql )

    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    records =[]
    if len(result) == 0:
        logger.info("No items in filesystem playlist")
    for row in result:
        #records.append( { 'location':urllib.url2pathname(row[0]), 'time':999, 'seconds':919 } )
        records.append( { 'location': row[1], 'id': row[0] } )
    return records

def renamer(tracks):
    tracks = get_whitespace_tracks()
    for track in tracks:
        location = track['location']
        tr_id = track['id']
        filepath = config.musicPath + location
        print filepath
        if isfile(filepath):
            newlocation = location.replace(' ', '_')

            sql = "UPDATE netjuke_tracks SET location = '%s' WHERE id = '%i'" % (newlocation, tr_id)
            cursor = db.cursor()
            cursor.execute(sql)

tracks = get_whitespace_tracks()
renamer(tracks)

"""
import urllib

#import ipdb;ipdb.set_trace()
t = get_whitespace_tracks()
print t
location = t[0]['location']
fd = open('/usr/local/media/'+location, 'r')
content = fd.readline()
fd.close()

print content
"""
