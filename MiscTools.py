#!/usr/bin/python
# -*- coding: utf-8 -*-

import  sys
sys.path.append('..')
from ErrorsHandler import *
import  LoadConfig
config = LoadConfig.LoadConfig()

import re
import  MySQLdb
from shutil import copy, move
from distutils.dir_util import copy_tree, create_tree
import os.path

from DB import DB
DB = DB()

def location2db(fullpath, rootDir):
    '''It will remove the /musicPath/userHome portion of the file location (its full path)'''

    regex = re.compile(config.musicPath)
    location = regex.sub('', fullpath)

    '''
    print "....................................... in location2db():"
    print "REGEX to remove: " + config.musicPath
    print "rootDir: " + rootDir
    print "fullpath: " + fullpath
    print "location: " + location
    '''

    return location

def getList(table):
    '''Get list from table and return it'''

    if table != 'licenses':
        table  = 'netjuke_' + table
        fields = ", comments, img_src"
    else: fields = ""

    db = DB.connect()
    sql = "SELECT id, name"+fields+" FROM " + table + " ORDER BY name"
    cursor = db.cursor()
    cursor.execute(sql)

    list = []

    result = cursor.fetchall()

    return result

def getIDbyLocation(location):
    db = DB.connect()
    cursor = db.cursor()

    sql = "SELECT id FROM netjuke_tracks WHERE location = '%s'" % location
    cursor.execute(sql)
    if cursor.rowcount > 0:
        return cursor.fetchone()[0]

def getID(table, value=None, create=True):
    '''
    Will get the ID from table where table.name = value.
    If value is empty, it will not be created, and 1 will be returned (which is N/A entry).
    If value is not found on table, it will be created and its ID will be returned.
    '''
    logger.debug99("called MiscTools.getID(table=%s, value=%s, create=%s)" % (table,value,str(create)) )

    # return 1 means N/A
    if (value == None) or (value == ''):
        #print "........... AT getID() WILL RETURN 1"
        return 1
    
    db = DB.connect()
    cursor = db.cursor()

    if table != "licenses": table = "netjuke_"+table

    sql = "SELECT id FROM "+table+" WHERE name = '%s'" % MySQLdb.escape_string(value.encode('utf8'))

    cursor.execute(sql)
    if cursor.rowcount > 0:
        return cursor.fetchone()[0]
    else:
        if create == True:
            return add2table(table, value)
        else:
            return 1

def add2table(table, value):
    if value == '': return
    db = DB.connect()
    cursor = db.cursor()

    if table is "licenses":
        return
    
    sql = 'INSERT INTO '+ table +' SET name = "%s", track_cnt = 1, home = ""' % MySQLdb.escape_string(value.encode('utf8'))
    cursor.execute(sql)
    logger.debug5("Adding '%s' to '%s' table " % (value, table) )

    return db.insert_id()

def removePathComponent(filepath, pathComponent):
    '''Removes pathComponent from filepath.'''

    regex = re.compile(pathComponent)
    newFile = regex.sub('', filepath)

    return newFile

def moveExactTree(file, target, spoolDir, noSpool=0):
    newFile = target + file
    if noSpool == 1:
        newFile = removePathComponent(newFile, spoolDir)

    newFileDir = os.path.dirname(newFile)

    if not os.path.exists(newFileDir):
	os.makedirs(newFileDir)

    if os.path.isfile(newFile):
        logger.info("* Trying to move file: %s to %s..." % (file, newFile))
        logger.info("* File is already there, skipping.. %s" % newFile)
        return newFile
    else:
        logger.info("Moving file: %s to %s..." % (file, newFile))
        move(file, newFile)
	os.chmod(newFile, 0755)

    return newFile

def copyExactTree(source, target, spoolDir, noSpool=0):
    '''
    Copy file using its exact same basedir as the tree to place into newRoot.
    If newRoot/file already exists, it will be skipped, otherwise copied.
    Intermediate directories will be created.
    '''
    
    newFile = target + source
    if noSpool == 1:
        newFile = removePathComponent(newFile, spoolDir)

    newFileDir = os.path.dirname(newFile)

    if not os.path.exists(newFileDir):
	os.makedirs(newFileDir)

    if os.path.isfile(newFile):
        logger.info("* Trying to copy file: %s to %s..." % (source, newFile))
        logger.info("* File is already there, skipping..")
        return newFile
    else:
        logger.info("in MiscTools.copyExactTree() Copying file: %s to %s..." % (source, newFile))
        copy(source, newFile)
        #print "* * * * * * DOING CHMOD on newFile: %s" % newFile
	os.chmod(newFile, 0755)

    return newFile

def cacheToSpool(source, spoolDir):
    '''Copy the source file to mpdir.'''

    # check if it is already in the spool
    if source.find(spoolDir) == 0:
        logger.info("source file is already on the spool, not copying again!")
        return source

    # target file inside the spool
    tmpfile = spoolDir + "/" + source

    if not os.path.isfile(tmpfile):
        tmpfile = copyExactTree(source, spoolDir, spoolDir)

    return tmpfile

# from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/498202
def QuoteForPOSIX(string):
    '''quote a string so it can be used as an argument in a  posix shell

       According to: http://www.unix.org/single_unix_specification/
          2.2.1 Escape Character (Backslash)

          A backslash that is not quoted shall preserve the literal value
          of the following character, with the exception of a <newline>.

          2.2.2 Single-Quotes

          Enclosing characters in single-quotes ( '' ) shall preserve
          the literal value of each character within the single-quotes.
          A single-quote cannot occur within single-quotes.

    '''

    return "\\'".join("'" + p + "'" for p in string.split("'"))

def get_ascii_filename(filename):
    return "".join([x for x in filename if ord(x) < 128])

def convert2ascii(s):
    #s = s.decode("utf-8").encode("ascii","replace")
    s = s.encode("ascii","ignore")
    return "ascii: " + s

def uniconvert(s, e):
    try:
        s = unicode(s,e)
    except UnicodeError:
        raise UnicodeError('bad filename: '+s)
    return s.encode('utf-8')

def uniconvert2(s=''):
    if (s == '') or (s is None): return ''
    try:
        s = unicode(s,'utf8') #+ " UTF"
    except Exception, e:
        try:
            s = unicode(s,'iso-8859-1') #+ " ISO"
        except:
            pass

    return s

def getTaggedMP3s(userInfo=None, fn=None):
    '''
    Get files that the user tagged and we have cached on the database
    '''

    db = DB.connect()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    sql = "SELECT * FROM mp3tmp WHERE 1"
    if userInfo is not None:
        sql += " AND uploader = '%i'" % userInfo['ID']
    if fn is not None:
        sql += " AND location = '%s'" % MySQLdb.escape_string(fn)
    sql += " AND imported = '0'"
    logger.debug4( "Getting list of cached/tagged MP3 files.." )
    logger.debug99( "Using SQL query: " + sql )
    cursor.execute(sql)
    result = cursor.fetchall()
    files = []
    for record in result:
        metadata = {}
        metadata['title'] = record['title']
        metadata['artist'] = record['artist']
        metadata['license'] = record['license']
        metadata['label'] = record['label']
        metadata['album'] = record['album']
        metadata['comment'] = record['comment']
        metadata['year'] = str(record['year'])
        metadata['genre'] = record['genre']
        metadata['tracknumber'] = str(record['tracknumber'])

        files.append( [ record['location'], metadata ])

    return files

def buildTags(metadata):
    tags = {'title'  : '',
            'artist'  : '',
            'album'   : '',
            'license' : '',
            'label'   : '',
            'comment' : ''
    }

    for tag in tags.keys():
        tag = tag.lower()
        val = metadata[tag]
        if (val != None) and (val != ''):
            metadata[tag] = unicode(val, 'utf8')

    return metadata

def convert2bitmap(img, w=300, h=300):
    pass
    """
    name, ext  = os.path.splitext(img)
    if ext == '':
       # in case we do not detect the extension, we return the default image
       img = config.webRoot + '/img/default.png'
       return wx.Image(img, wx.BITMAP_TYPE_PNG).Scale(w,h).ConvertToBitmap()

    if ext.lower() == '.png': return wx.Image(img, wx.BITMAP_TYPE_PNG).Scale(w,h).ConvertToBitmap()
    if ext.lower() == '.jpg': return wx.Image(img, wx.BITMAP_TYPE_JPEG).Scale(w,h).ConvertToBitmap()
    if ext.lower() == '.gif': return wx.Image(img, wx.BITMAP_TYPE_GIF).Scale(w,h).ConvertToBitmap()
    if ext.lower() == '.bmp': return wx.Image(img, wx.BITMAP_TYPE_BMP).Scale(w,h).ConvertToBitmap()
    """


"""
  html2text.py

  convert an html doc to text

"""


# system libraries
import os, sys, string, time, getopt
import re

WIDTH = 80

def tag_replace (data,center,indent, use_ansi = 0):
  data = re.sub ("\s+", " ", data)
  data = re.sub ("(?s)<!--.*?-->", "", data)
  data = string.replace (data, "\n", " ")
  output = []

  # modified 6/17/99 splits on all cases of "img" tags
  # imgs = re.split ("(?s)(<img.*?>)", data)
  imgs = re.split ("(?si)(<img.*?>)", data)

  for img in imgs:
    if string.lower(img[:4]) == "<img":
      alt = re.search ("(?si)alt\s*=\s*\"([^\"]*)\"", img)
      if not alt:
        alt = re.search ("(?si)alt\s*=([^\s]*)", img)
      if alt:
        output.append ("%s" % img[alt.start(1):alt.end(1)])
      else:
        output.append ("[img]")
    else:
      output.append (img)
  data = string.join (output, "")
  data = re.sub ("(?i)<br>", "\n", data)
  data = re.sub ("(?i)<hr[^>]*>", "\n" + "-"*50 + "\n", data)
  data = re.sub ("(?i)<li>", "\n* ", data)
  if use_ansi:
    data = re.sub ("(?i)<h[0-9]>", "\n[32m", data)
  else:
    data = re.sub ("(?i)<h[0-9]>", "\n", data)
  if use_ansi:
    data = re.sub ("(?i)</h[0-9]>", "[0m\n", data)
  else:
    data = re.sub ("(?i)</h[0-9]>", "\n", data)
  data = re.sub ("(?i)<ul>", "\n<UL>\n", data)
  data = re.sub ("(?i)</ul>", "\n</UL>\n", data)
  data = re.sub ("(?i)<center>", "\n<CENTER>\n", data)
  data = re.sub ("(?i)</center>", "\n</CENTER>\n", data)
  if use_ansi:
    data = re.sub ("(?i)<b>", "[1m", data)
    data = re.sub ("(?i)</b>", "[0m", data)
    data = re.sub ("(?i)<i>", "[2m", data)
    data = re.sub ("(?i)</i>", "[0m", data)
    data = re.sub ("(?i)<title>", "\n<CENTER>\n[31m", data)
    data = re.sub ("(?i)</title>", "[0m\n</CENTER>\n", data)
  else:
    data = re.sub ("(?i)<title>", "\n<CENTER>\n", data)
    data = re.sub ("(?i)</title>", "\n</CENTER>\n", data)
  data = re.sub ("(?i)<p>", "\n", data)
  data = re.sub ("(?i)<tr[^>]*>", "\n", data)
  data = re.sub ("(?i)</table>", "\n", data)
  data = re.sub ("(?i)<td[^>]*>", "\t", data)
  data = re.sub ("(?i)<th[^>]*>", "\t", data)
  data = re.sub (" *\n", "\n", data)
  lines = string.split (data, "\n")
  output = []
  for line in lines:
    if line == "<UL>":
      indent = indent + 1
    elif line == "</UL>":
      indent = indent - 1
      if indent < 0: indent = 0
    elif line == "<CENTER>":
      center = center + 1
    elif line == "</CENTER>":
      center = center - 1
      if center < 0: center = 0
    else:
      if center:
        line = "  "*indent + string.strip(line)
        nline = re.sub("\[.*?m", "", line)
        nline = re.sub ("<[^>]*>", "", nline)
        c = WIDTH/2 - (len (nline) / 2)
        output.append (" "*c + line)
      else:
        output.append ("  "*indent + line)
  data = string.join (output, "\n")
  data = re.sub (" *\n", "\n", data)
  data = re.sub ("\n\n\n*", "\n\n", data)
  data = re.sub ("<[^>]*>", "", data)
  return (data, center, indent)

def html2text (data, use_ansi = 0, is_latin1 = 0):
  return data
  pre = re.split("(?s)(<pre>[^<]*</pre>)", data)
  out = []
  indent = 0
  center = 0
  for part in pre:
    if part[:5] != "<pre>":
      (res, center, indent) = tag_replace (part,center,indent, use_ansi)
      out.append (res)
    else:
      part = re.sub("(?i)</*pre>", "", part)
      out.append (part)
  data = string.join (out)
  data = re.sub ("&gt;", ">", data)
  data = re.sub ("&lt;", "<", data)
  data = re.sub ("&nbsp;", " ", data)
  if is_latin1:
    data = re.sub ("&copy;", "©", data)
    data = re.sub ("&eacute;", "é", data)
    data = re.sub ("&egrave;", "è", data)

  return data

def RetPyData(item, tree):
    logmsg = "RetPyData() called with tree: '%s'" % tree
    logger.debug(logmsg)
    return

    if tree is 'MusicTree':
        itemData = frame.MusicPanel.MusicTree.GetPyData(item)
    elif tree is 'NewMusicTree':
        itemData = frame.MusicPanel.NewMusicTree.GetPyData(item)
    elif tree is 'ReportsTree':
        itemData = frame.MusicPanel.ReportsTree.GetPyData(item)
    elif tree is 'Playlist':
        itemData = frame.Playlist.GetPyData(item)
    else:
        logger.debug("No tree selected ... returning silently")
        return []

    if not itemData: return ['null']

    itemType = itemData[0]

    dataArray = []
    if (itemType == 'song' or itemType == 'report'):
        itemID = itemData[1]
        logmsg = "itemID = %s" % itemID
        logger.debug(logmsg)
        itemLocation = itemData[2]
        itemLocationNew = itemData[3]
        itemLength = itemData[4]
        dataArray.append(itemType)
        dataArray.append(itemID)
        dataArray.append(itemLocation)
        dataArray.append(itemLocationNew)
        dataArray.append(itemLength)
    elif itemType == 'album':
        itemID = itemData[1]
        dataArray.append(itemType)
        dataArray.append(itemID)
    elif itemType == 'artist':
        itemID = itemData[1]
        dataArray.append(itemType)
        dataArray.append(itemID)
    elif itemType == 'genre':
        itemID = itemData[1]
        dataArray.append(itemType)
        dataArray.append(itemID)
    elif itemType == 'label':
        itemID = itemData[1]
        dataArray.append(itemType)
        dataArray.append(itemID)
    elif itemType == 'playlist':
        itemID = itemData[1]
        dataArray.append(itemType)
        dataArray.append(itemID)
    elif itemType == 'ReportLabel': # which is = artist for music
        itemID = itemData[1]
        dataArray.append(itemType)
        dataArray.append(itemID)
    elif itemType == 'ReportTopic': # which is = album for music
        itemID = itemData[1]
        dataArray.append(itemType)
        dataArray.append(itemID)
	
    return dataArray
   
def ValidateImage(img, type):
    #print "VALIDATING: %s TYPE: %s" % (img, type)
    if img is None or img == '': return ''
    else:
        if type is 'label' : type = 'la'
        if type is 'artists': type = 'la'
        if type is 'albums' : type = 'ar'
        if type is 'tracks'  : type = 'al'

        newImg = config.musicPath + img
        oldImg = config.webRoot + '/img/' + type + '/' + img

        if os.path.isfile(newImg):
            return newImg
        elif os.path.isfile(oldImg):
            return oldImg
        else: return False

def saveToDB(data):
    if data['type'] == '': return

    #itemID = getID(data['type'], data['name'], False)

    data['img_src'] = removePathComponent(data['img_src'], config.musicPath)

    table = "netjuke_"+data['type'] + "s"

    sql = "UPDATE "+table+" SET "

    i = 0
    sep = ", "
    for key in data:
	if (key is not 'type') and (key is not 'id'):
            sql += key + " = '%s'" % MySQLdb.escape_string(data[key].encode('utf8'))
            if (i < len(data)-1): sql += sep
	i = i+1

    sql += " WHERE id = '%i'" % data['id']

    db = DB.connect()
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        return True
    except Exception, e: logger.error("Running SQL: %s got EXCEPTION: %s" % (sql,str(e)))

