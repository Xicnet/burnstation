#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.append("..")
from ErrorsHandler import *


import httplib, urllib
    
class Jamendo(object):

    def __init__(self):
        self.base_url = "www.jamendo.com"
        self.type     = "artists"

    def __ua__(self, url):
        "user agent for fetching data from jamendo, return list"
        conn = httplib.HTTPConnection(self.base_url)
        conn.request("GET", url)
        r1 = conn.getresponse()
        if r1.status == 200:
            # return a list, splited by newline
            return r1.read().split("\n")
        else:
            return False

    def get_all_artists(self):
        " returns a list with dicts with (id, name) "
        #TODO: code it
        pass

    def search_artist_by_name(self, search):
        " returns list with artists ID(s) from search "
        l = []
        id_list = self.__ua__(url="/get/artist/search/artist/id/plain/%s" % search)
        title_list  = self.__ua__(url="/get/artist/search/artist/title/plain/%s" % search)
        for i in range(len(id_list)):
            l.append({ 'id' : id_list[i], 'name' : title_list[i], 'img' : 'img', 'info' : 'info' })
        return l

    def get_albums_from_artist(self, artist_id):
        "returns a list with dicts with (id, title) for artist_id"
        l = []
        id_list     = self.__ua__(url="/get/album/id/artist/id/plain/%s" % artist_id)
        title_list  = self.__ua__(url="/get/album/id/artist/title/plain/%s" % artist_id)
        for i in range(len(id_list)):
            l.append({ 'id' : id_list[i], 'name' : title_list[i], 'img': 'img', 'info':'info'})
        return l

    def get_tracks_from_album(self, album_id):   
        "returns a list with dicts with (id, title) for album_id"
        l = []
        title_list  = self.__ua__(url="/get/track/id/album/title/plain/%s" % album_id)
        id_list     = self.__ua__(url="/get/track/id/album/id/plain/%s" % album_id)
        for i in range(len(id_list)):
            location = self.get_musicfile_URL(id_list[i])
            l.append({ 'id' : id_list[i], 'name' : title_list[i], 'img': 'img', 'info':'info', 'location':location })
        return l    
    
    def get_musicfile_URL(self, track_id):
        " returns URL for musicfile "
        #return "http://www.jamendo.com/get/track/id/track/audio/plain/%s" % track_id
        return self.__ua__("http://www.jamendo.com/get/track/id/track/audio/plain/%s" % track_id)[0]
        
    def get_artwork_URL(self, album_id, size=300):
        " returns URL to album cover from album id, size (25|50|100|200|300|400) px "
        return "http://www.jamendo.com/get/album/id/album/artworkurl/redirect/%s/?artwork_size=%s" % (album_id, size)        

    def descend(self, parent, selected):
        " returns child items from selected parent "
        logger.debug("*********** Trying to descend from type: %s" % self.type)
        if self.type == 'artists':
            self.type = 'albums'
            logger.info("*** jamendo: browsing albums")
            logger.debug("*********** type: %s" % self.type)
            return self.get_albums_from_artist(parent)
        elif self.type == 'albums':
            self.type = 'tracks'
            logger.info("**** jamendo: browsing tracks!!!")
            return self.get_tracks_from_album(parent)
        elif self.type == 'tracks':
            self.type = 'tracks'
            logger.info("jamendo: playing track")
            raise Exception, "Trying to Play this track"
    
"""
j = Jamendo()
print j.get_tracks_from_album(album_id=14074)
print j.get_albums_from_artist(artist_id=2519)
print j.get_musicfile_URL(track_id=111582)
print j.get_artwork_URL(album_id=14074, size=300)
"""
#print j.search_artist_by_name(search="")
