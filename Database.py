#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb
import  sys
sys.path.append('..')
import  LoadConfig
config = LoadConfig.LoadConfig()

import urllib
from MiscTools import *

db = MySQLdb.connect(host=config.DBhost, user=config.DBuser, passwd=config.DBpass, db=config.DB)
db.set_character_set('utf8')

#--------------------------------------------------------------------
def GetLabels(searchString=''):
    sql  = "SELECT DISTINCT la.id, la.name, la.img_src, la.comments"
    sql += " FROM netjuke_labels la, netjuke_tracks tr"
    sql += " WHERE la.id=tr.la_id AND tr.report=0"
    sql += " AND la.exclude = 'f' AND tr.exclude = 'f'"
    sql += " AND la.name LIKE '%"
    sql += "%s" % searchString
    sql += "%'" + " ORDER BY la.name"

    #logger.debug5( sql )

    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    records =[] 
    for row in result:
        records.append({ 'id':row[0], 'name':uniconvert2(row[1]), 'img':row[2], 'info':row[3] })

    return records

#--------------------------------------------------------------------
def GetArtists(labelID):

    #logger.debug( "* Getting ARTISTS for LABEL: %i" % labelID )

    sql = "/* Get ARTISTS for this LABEL */ \
            SELECT DISTINCT ar.id id, ar.name name, ar.img_src, ar.comments \
            FROM netjuke_artists ar, netjuke_tracks tr, netjuke_labels la, \
            netjuke_albums al \
            WHERE tr.la_id=la.id \
            AND ar.id=tr.ar_id \
            AND al.id=tr.al_id"
    sql += " AND la.id=%s" % labelID
    sql += " AND tr.report=0"
    sql += " AND ar.exclude = 'f' AND la.exclude = 'f' AND tr.exclude = 'f'"
    sql += " ORDER BY name"

    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    records =[] 
    for row in result:
        records.append({ 'id':row[0], 'name':uniconvert2(row[1]), 'img':row[2], 'info':row[3] })

    return records

#--------------------------------------------------------------------
def GetAlbums(labelID, artistID):
    #logger.debug( "* Getting ALBUMS for LABEL: %i and ARTIST: %i" % (labelID, artistID) )
    sql = "SELECT DISTINCT al.id id, al.name album, al.img_src, al.comments" \
        + " FROM netjuke_artists ar, netjuke_albums al, netjuke_tracks tr," \
        + " netjuke_labels la" \
        + " WHERE tr.ar_id=ar.id AND tr.al_id=al.id AND" \
        + " ar.id=" + str(artistID) \
        + " AND tr.la_id=la.id" \
        + " AND tr.la_id=" + str(labelID) \
        + " AND tr.report=0" \
        + " AND ar.exclude = 'f' AND al.exclude = 'f' AND la.exclude = 'f' AND tr.exclude = 'f'" \
        + " ORDER BY album" 
    
    #logger.debug( sql )

    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    records =[] 
    for row in result:
        records.append({ 'id':row[0], 'name':uniconvert2(row[1]), 'img':row[2], 'info':row[3] })

    return records

#--------------------------------------------------------------------
def GetTracks(labelID, artistID, albumID):
    sql = "SELECT DISTINCT tr.id id, tr.name track, tr.location location, al.img_src, tr.comments, tr.time, time_format(sec_to_time(sum(tr.time)), \"%H:%i:%S\")" \
        + " FROM netjuke_artists ar, netjuke_albums al, netjuke_tracks tr," \
        + " netjuke_labels la" \
        + " WHERE tr.ar_id=ar.id AND tr.al_id=al.id AND tr.la_id=la.id" \
        + " AND tr.la_id=" + str(labelID) \
        + " AND ar.id=" + str(artistID) \
        + " AND tr.al_id=" + str(albumID) \
        + " AND tr.report=0" \
        + " AND ar.exclude = 'f' AND al.exclude = 'f' AND la.exclude = 'f' AND tr.exclude = 'f'" \
        + " GROUP BY tr.id" \
        + " ORDER BY tr.track_number" 
    
    #logger.debug( sql )

    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    records =[] 
    for row in result:
        time = " [" + str(row[6]) + "]"
        records.append({ 'id':row[0], 'name':uniconvert2(row[1]) + time, 'location':config.musicPath+row[2], 'img':row[3], 'info':row[4], 'seconds':row[5], 'time':time })

    return records

#--------------------------------------------------------------------
def CreatePlaylist():
    '''Create a new playlist. First checking that no playlist-recovery is needed.

       Returns the ID of the new playlist or the or the ID of a playlist to recover.'''

    # check if there is a playlist flagged for recovery before creating a new one
    sql = "SELECT id FROM netjuke_plists WHERE recover = 1"
    cursor = db.cursor()
    cursor.execute(sql)
    row = None
    row = cursor.fetchone()
    if row is not None: 
        playlistID = row[0]
    else:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        cursor = db.cursor()
        cursor.execute("INSERT INTO netjuke_plists SET title='New Playlist', us_email=%s, created=now()", (timestamp))
        playlistID = db.insert_id()

    return playlistID

#--------------------------------------------------------------------
def GetPlaylist(playlistID):
    sql = "SELECT pl.tr_id, tr.name, tr.location, tr.time, " 
    sql += '''time_format(sec_to_time(sum(tr.time)), \"%H:%i:%S\")'''
    sql += " FROM netjuke_plists_tracks pl, netjuke_tracks tr " \
           " WHERE pl.pl_id = %i AND pl.tr_id=tr.id" \
           " GROUP BY pl.id ASC" \
           " ORDER BY pl.id ASC" % playlistID
    
    #logger.debug( sql )

    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    records =[]
    if len(result) == 0:
        logger.info("GetPlaylist: No items in playlist #%i" % playlistID)
        result = [ ['', 'empty', '', '', ''] ]
    for row in result:
        if row[4] is not '': time = " [" + str(row[4]) + "]"
        else: time = ''
        records.append({ 'id':row[0], 'name':uniconvert2(row[1]) + time, 'location':urllib.url2pathname(config.musicPath+row[2]), 'img':str(row[0]), 'seconds':row[3], 'time':time })

    return records

#--------------------------------------------------------------------
def GetFilesystemPlaylist(playlistID):
    sql = "SELECT id, tr_name, tr_location" \
          " FROM fs_playlist" \
          " WHERE pl_id = %i" \
          " ORDER BY id ASC" % playlistID
    
    #logger.debug( sql )

    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    records =[]
    if len(result) == 0:
        logger.info("No items in filesystem playlist")
        result = [ ['', 'empty', '', ''] ]
    for row in result:
        records.append({ 'id':row[0], 'name':uniconvert2(row[1]), 'location':urllib.url2pathname(row[2]), 'time': 999, 'img':'img' })

    return records

#--------------------------------------------------------------------
def AddToPlaylist(trackID, playlistID):
    sql = "INSERT IGNORE INTO netjuke_plists_tracks SET tr_id=%s, pl_id=%s" % (trackID, playlistID)
    #logger.debug( sql )

    cursor = db.cursor()
    cursor.execute(sql)

#--------------------------------------------------------------------
def AddToFilesystemPlaylist(track_name, track_location, playlistID):
    sql = "INSERT IGNORE INTO fs_playlist SET tr_name='%s', tr_location='%s', pl_id=%s" % (track_name, track_location, playlistID)
    logger.debug( sql )

    cursor = db.cursor()
    cursor.execute(sql)

#--------------------------------------------------------------------
def RemoveFromFilesystemPlaylist(track_location, playlistID=0):
    """Remove trackID from playlistID"""
    sql = "DELETE FROM fs_playlist WHERE tr_location = '%s' AND pl_id='%i'" % (track_location, playlistID)
    #logger.debug( sql )
    cursor = db.cursor()
    cursor.execute(sql)

#--------------------------------------------------------------------
def RemoveFromPlaylist(trackID=0, playlistID=0):
    """Remove trackID from playlistID"""

    if trackID == '' or playlistID == '': return
    sql = "DELETE FROM netjuke_plists_tracks WHERE tr_id = '%i' AND pl_id='%i'" % (int(trackID), int(playlistID))
    #logger.debug( sql )
    cursor = db.cursor()
    cursor.execute(sql)

#--------------------------------------------------------------------
def PublishPlaylist(playlistID, user, label):
    logger.debug( "Publishing playlist #%i for user '%s' into '%s' label" % (playlistID, user, label) )
    files = GetFilesystemPlaylistTracks(playlistID)
    for file in files:
        logger.info("Publishing: %s" % file['location'])
        cmd = "python publish/publisher.py '%s' '%s' '%s'" % (file['location'], user, label)
        os.system(cmd)

#--------------------------------------------------------------------
def GetFilesystemPlaylistTracks(playlistID):
    sql = "SELECT tr_location FROM fs_playlist WHERE pl_id=%s" % (playlistID)
    #logger.debug( sql )

    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    records =[]
    if len(result) == 0:
        logger.info("No items in filesystem playlist")
    for row in result:
        records.append( { 'location':urllib.url2pathname(row[0]), 'time':999, 'seconds':919 } )

    return records

#--------------------------------------------------------------------
def Auth(user, password):
    sql = "SELECT id FROM netjuke_users WHERE email = '%s' AND password = md5('%s')" % (user, password)
    logger.debug( sql )

    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    if len(result) == 0:
        logger.info("Invalid user or password!")
        return False
    else:
        logger.info("User '%s' logged login!" % user)
        return True

#--------------------------------------------------------------------
def Register(name, email, password):
    sql = "INSERT INTO netjuke_users SET name = '%s', nickname = '%s', email = '%s', password = md5('%s')" % (name, name, email, password)
    logger.debug( sql )

    cursor = db.cursor()
    cursor.execute(sql)
    logger.info("Registered user '%s' into DB" % name)
    return True

#--------------------------------------------------------------------
def GetMediaFiles():
    sql = "SELECT location FROM netjuke_tracks";
    logger.debug( sql )

    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    records =[]
    for row in result:
        records.append( { 'location':urllib.url2pathname(row[0]) } )
    return records

