import os, sys

import Database
from MiscTools import *
sys.path.append(os.getcwd()+"/plugins")
sys.path.append(os.getcwd()+"/plugins/jamendo")
sys.path.append(os.getcwd()+"/publish")

from jamendo import *

from AudioFile import AudioFile


class Browser:
    '''
    The browser object returns an array of items, typically to be used
    by the scroller object from the Burn Station.
    
    It should also provide a series of methods to browse back and forth
    through the child/parent items.
    '''
    #--------------------------------------------------------------------
    def __init__(self, level='', itemID=0):
        self.level = level
        self.itemID = itemID
        self.j = Jamendo()
        logger.debug( "******** level: " + level)

    #--------------------------------------------------------------------
    def SetType(self, type):
        self.level = type

    #--------------------------------------------------------------------
    def getList(self, parent=0, index=0):
        if self.level == "path": return self.getListFromPath(parent, index)
        elif self.level == "jamendo": return self.getListFromJamendo(parent, index)
        elif self.level == "labels": return self.getListFromDB(parent, index)
        else: return self.getListFromDB(parent, index)

    #--------------------------------------------------------------------
    def getListFromJamendo(self, parent, index=0):
        return self.j.search_artist_by_name(search="")

    #--------------------------------------------------------------------
    def getListFromPath(self, parent, index=0):
        logger.debug( "Getting contents from: %s" % parent )
        try:
            if parent == 0: parent = "/"
            dirlist = os.listdir(parent)
            dirlist.sort()
        except Exception, e: logger.error( "at Browser.getListFromPath(): " + str(e) )

        list = []

        for x in dirlist:
            name, ext  = os.path.splitext(x)

            if x != get_ascii_filename(x):
                continue

            real_path = os.path.join(parent, uniconvert2(x))
            if os.path.isfile(real_path):
                if ext.lower() == '.ogg' or ext.lower() == '.mp3':
                    # read vorbis info
                    self.af = AudioFile(real_path)
                    time = int(self.af.getLength())
                    length = " (" + str(time) + ")"
                    list.append( {'location':real_path, 'id':'idd', 'img':'imgg', 'name': x + length, 'time': time, 'seconds':time } )
            else:
                list.append( {'location':real_path, 'id':'idd', 'img':'imgg', 'name': "/" + x } )

        return list

    #--------------------------------------------------------------------
    def getListFromDB(self, itemID=0, index=0):
        #print "AT GET LIST FROM DB:::::::::::::::" + self.level + "::" + str(itemID) + '::' + str(index) + "::"
        '''Get the list of items to be displayed'''

        if self.level == 'labels':
            logger.debug5( "GETTING LABELS" )
            items = Database.GetLabels()
            self.level   = 'artists'
        elif self.level == 'artists' and itemID>0:
            logger.debug5( "GETTING ARTISTS" )
            items = Database.GetArtists(itemID)
            self.labelID = itemID
            self.labelIndex = index
            self.level   = 'albums'
        elif self.level == 'albums':
            logger.debug5( "GETTING ALBUMS" )
            items = Database.GetAlbums(self.labelID, itemID)
            self.level = 'tracks'
            self.artistID = itemID
            self.artistIndex = index

        elif self.level == 'tracks':
            logger.debug5( "GETTING TRACKS" )
            items = Database.GetTracks(self.labelID, self.artistID, itemID)
            self.albumID = itemID
            self.albumIndex = index
            self.level = 'tracks_list'
        elif self.level == 'tracks_list':
            raise Exception, "Trying to open track means PLAY IT !"

        elif self.level == 'playlist' or self.level == 'playlist_tracks':
            logger.debug5( "GETTING DB PLAYLIST TRACKS" )
            if itemID == 0 and self.itemID > 0 : itemID = self.itemID
            items = Database.GetPlaylist(itemID)
            self.level = 'playlist_tracks'

        elif self.level == 'fs_playlist':
            logger.debug5( "GETTING FILESYSTEM PLAYLIST TRACKS" )
            if itemID == 0 and self.itemID > 0 : itemID = self.itemID
            items = Database.GetFilesystemPlaylist(itemID)
            self.level = 'fs_playlist'

        try: return items
        except: return [ { 'id':"a", 'name':"a", 'img':"a", 'info':"a" } ]

    #--------------------------------------------------------------------
    def descend(self, parent, selected):
        self.parentIndex = selected
        if self.level == 'jamendo':
            return self.j.descend(parent, selected)
        elif self.level == 'path':
            # browsing filesystem
            logger.debug( "Descend to: " + parent )
            if os.path.isdir(parent):
                self.currentDir = parent
                return self.getList(parent, selected)
            else:
                self.Play()
        elif self.level != 'path' and self.level != '' and self.level != 'playlist_tracks':
            # browsing database
            return self.getList(parent, selected)
        else:
            # no childs, impossible to descend
            raise Exception, "Descend() impossible. No child items found!"

    #--------------------------------------------------------------------
    def Back(self):
        print "BACK FROM TRACKS, self.level = " + self.level
        if self.level == 'path':
            dir = self.currentDir+'/..'
            logger.debug(" ********** currentDir: "+dir)
            items = self.getList(dir, self.parentIndex)
            self.currentDir = dir
            return { 'list':items, 'index':self.parentIndex }
        elif self.level == 'tracks_list':
            items = Database.GetAlbums(self.labelID, self.artistID)
            self.level = 'tracks'
            return { 'list':items, 'index':self.albumIndex }
        elif self.level == 'tracks':
            items = Database.GetArtists(self.labelID)
            self.level   = 'albums'
            return { 'list':items, 'index':self.artistIndex }
        elif self.level == 'albums':
            items = Database.GetLabels()
            self.level = 'artists'
            return { 'list':items, 'index':self.labelIndex }
        else: return

