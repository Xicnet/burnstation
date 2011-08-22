#!/bin/env python
# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
import math
import time

import Database

import pygame
import pygame.joystick
import pygame.display

import os, os.path
from MiscTools import *
import urllib
import random

from Browser import *
from text import *

from globals import *

import Socket

pygame.display.init()
pygame.joystick.init() #initialize joystick module
pygame.joystick.get_init() #verify initialization (boolean)

#################################################3
from itertools import chain

def truncline(text, font, maxwidth):
    real=len(text)
    stext=text
    l=font.size(text)[0]
    cut=0
    a=0
    done=1
    old = None
    while l > maxwidth:
        a=a+1
        n=text.rsplit(None, a)[0]
        if stext == n:
            cut += 1
            stext= n[:-cut]
        else:
            stext = n
        l=font.size(stext)[0]
        real=len(stext)
        done=0
    return real, done, stext

def wrapline(text, font, maxwidth):
    done=0
    wrapped=[]

    while not done:
        nl, done, stext=truncline(text, font, maxwidth)
        wrapped.append(stext.strip())
        text=text[nl:]
    return wrapped


def wrap_multi_line(text, font, maxwidth):
    """ returns text taking new lines into account.
    """
    lines = chain(*(wrapline(line, font, maxwidth) for line in text.splitlines()))
    return list(lines)

#############################################

def load_image(name, colorkey=None):
    fullname = name
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        logger.debug( "Cannot load image:" + name )
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

#--------------------------------------------------------------------
class FontCache:
    def __init__(self, face, size):
        self.face = face
        self.size = size
        self.cache = {}

        num_joysticks = pygame.joystick.get_count()
        if num_joysticks > 0:
            self.stick = pygame.joystick.Joystick(0)
            self.stick.init() # now we will receive events for the joystick

    #--------------------------------------------------------------------
    def get(self, scale):
        font = self.cache.get(scale)
        if font is None:
            font = self.cache[scale] = pygame.font.Font(self.face, int(round(self.size * scale)))
        return font

#--------------------------------------------------------------------
class Textbox(pygame.sprite.Sprite):
    """
    Scrolling wheel on a line-by-line array of elements.
    The scrolling happens by increasing and decreasing the array index.
    
    Arguments it takes are:

    browser - the object which contains the list of items to be scrolled
    surface - where the scroller should be rendered
    posX - horizontal position
    bgcolor - background color
    fontsize - for the selected line
    visibles - how many elements are visible
    """
    def __init__(self, group, text, surface, posX, posY, bgcolor, fontsize, visibles, w, h, scrollbar=True):
        pygame.sprite.Sprite.__init__(self, group)

        self.items=[]

        self.text = text
        self.scrollbar = scrollbar

        # select first item to start
        self.selected   = 0

        self.fontsize   = fontsize
        self.visibles   = visibles
        self.fontcache  = FontCache(None, self.fontsize)
        self.subiendo   = 0
        self.bajando    = 0
        self.speed      = 0
        self.mustRender = False
        self.posX       = posX
        self.posY       = posY
        self.bgcolor    = bgcolor
        self.playtime = 0

        self.w = w
        self.h = h

        #self.image = surface

        self.BrowserInit(text)

        self.mustRender = True

        self.action   = {}

        # arrow down
        self.action[274] = self.goDown
        # arrow up
        self.action[273] = self.goUp
        # arrow left
        self.action[275] = self.BrowseForward
        # arrow left
        self.action[276] = self.BrowseBack
        # a
        self.action[97] = self.AddToRemoveFromPlaylist

    #--------------------------------------------------------------------
    def BrowserInit(self, text):
        self.image = pygame.Surface((self.w,self.h))
        self.image = self.image.convert()
        self.image.fill(BLACK)

        #self.rect = self.image.get_rect()

        self.text = text
        #self.list  = self.browser.getList([{'name': 'lala'}], 0)
        self.list  = text

        for record in self.list:
            self.items.append(record)
        self.Redraw()

    #--------------------------------------------------------------------
    def SetText(self, text):
        if text:
            font = self.fontcache.get(1)
            #self.text = wrapline(text.replace("\r", ""), font, 300)  #.split("\n")
            self.text = text.replace("\r", "").split("\n")
        else:
            self.text = "nada"

    #--------------------------------------------------------------------
    def Refresh(self):
        self.list  = self.text
        self.Redraw()
        logger.debug( "Refresh called" )

    #--------------------------------------------------------------------
    def Redraw(self, index=-1):
        self.items=[]
        for record in self.list:
            self.items.append(record)

        if len(self.items) == 0:
            logger.error("No items returned, nothing to Redraw(). Stopping here!")
            return

        self.getSelected(self.list, index)
        self.mustRender = True

    #--------------------------------------------------------------------
    def getSelected(self, list, index=-1):
        if index > -1: self.selected = index
        else:
            #if self.browser.level != 'tracks': self.selected = 0
            self.selected = 0

    #--------------------------------------------------------------------
    def goUp(self):
        self.keystart = time.time()
        self.selected -= 1
        self.speed     = -1.0
        self.mustRender = True
        self.itemID = self.list[self.selected]['id']

    #--------------------------------------------------------------------
    def goDown(self):
        self.keystart = time.time()
        self.selected += 1
        self.speed     = 1.0
        try: self.itemID = self.list[self.selected]['id']
        except Exception, e:
            logger.warn("EXCEPTION: %s" % str(e))
            self.selected = 0
            self.itemID = self.list[self.selected]['id']
        self.mustRender = True

    #--------------------------------------------------------------------
    def stopMoving(self):
        self.speed     = 0.0
        self.selected = int(round(self.selected))

    #--------------------------------------------------------------------
    def BrowseForward(self):
        self.itemID = self.list[self.selected]['id']
        if self.browser.level == 'path': parent = self.list[self.selected]['location']
	else: parent = self.itemID
        try:
            self.list = self.browser.descend(parent, self.selected)
            self.Redraw()
        except Exception, e:
            logger.debug("Browser exception: " + str(e))
            logger.debug("Browser not descending, trying to PLAY")
            #self.Play()
            raise Exception, "PLAY TRACK"


    #--------------------------------------------------------------------
    def BrowseBack(self):
        if self.browser.level != 'labels' and self.browser.level != 'playlist_tracks':
            goBack = self.browser.Back()
            try:
                self.list = goBack['list']
                self.Redraw(goBack['index'])
            except: logger.warn("Cannot go back")

    #--------------------------------------------------------------------
    def AddToRemoveFromPlaylist(self, playlistID):
        selected = self.list[self.selected]
        if self.browser.level == 'tracks_list':
            logger.info( "Adding track to playlist" )
            Database.AddToPlaylist(selected['id'], playlistID)

        elif self.browser.level == 'playlist_tracks':
            logger.info("Deleting track from playlist")
            Database.RemoveFromPlaylist(selected['id'], playlistID)

        elif self.browser.level == 'fs_playlist':
            logger.info("Deleting track from filesystem playlist")
            Database.RemoveFromFilesystemPlaylist(selected['location'], playlistID)

        elif self.browser.level == 'path':
            logger.info( "Adding track to filesystem playlist" )
            logger.debug5("************ at AddToRemoveFromPlaylist() , selected: %s" % selected)
            from publish.RecursiveParser import RecursiveParser
            if os.path.isdir(selected['location']):
                # if selection is a directory, add files recursively
                parser = RecursiveParser()
                supportedFormats = ['ogg']
                files = parser.getRecursiveFileList(selected['location'], supportedFormats)
                for file in files:
                    Database.AddToFilesystemPlaylist(os.path.basename(file), file, playlistID)

            Database.AddToFilesystemPlaylist(selected['name'], selected['location'], playlistID)

        else: logger.info( "Not a track (self.browser.level = %s) .. not adding to playlist" % self.browser.level )


    #--------------------------------------------------------------------
    def Next(self):
        print self.list[self.selected+1]['location']

    #--------------------------------------------------------------------
    def update(self):
        if self.mustRender:
            self.render()
            self.mustRender = False

    #--------------------------------------------------------------------
    def getLabel(self, number):
        number = int(round(number))
        if number < 0 or number >= len(self.items):
            return
        return self.items[number]

    #--------------------------------------------------------------------
    def render(self):
        self.image.fill(self.bgcolor)
        #logger.debug5( "at scroller.render(): " + self.browser.level )

        def unaLinea(n, seleccionado=0):
            a = self.getLabel(self.selected+n)
            if a is None:
                return

            o = n * (0.7/self.visibles)
            j = n * (1.0/self.visibles)
            v = 255*(1-math.sin((math.fabs(j))*math.pi/2))
            color = (10,200,10) 
            font = self.fontcache.get(1)
            t = font.render( a, 1, color)
            deltay = n*self.fontsize*(0.6)
            #self.posX = random.randint(30,40)
            #self.image.blit(t, t.get_rect(left=self.image.get_rect().left+self.posX, centery=self.image.get_rect().centery+ deltay ) )
            self.image.blit(t, t.get_rect(left=self.image.get_rect().left+self.posX, centery=20+ deltay ) )

        if self.selected < 0:
            self.selected = 0
        if self.selected >= len(self.items):
            self.selected = len(self.items)-1

        for n in range(self.visibles, 0, -1):
            unaLinea(-n)
            unaLinea(n)
        unaLinea(0,1)

        if self.scrollbar:
            self.image.fill(BARDARK, self.image.get_rect(left=10, width=10))
            barheight = 10
            barrect = self.image.get_rect(left=10, width=10, height=barheight)
        try:
            ratio = float(self.selected) / len(self.items)
        except Exception, e:
            logger.error("scroller EXCEPTION: " + str(e))
            return
        if self.scrollbar:
            barrect.top = (self.image.get_rect().height-barheight) * ratio
            self.image.fill(BARLIGHT, barrect)

        # FIXME make screenshot callable via keystroke
        #pygame.image.save(self.image, "/tmp/bs2.0.png")
        #logger.debug("rendered scroller")

    #--------------------------------------------------------------------
    def SetFocus(self, state):
        if state: self.SetSelected()
        else: self.SetUnSelected()
        self.isFocused = state

    #--------------------------------------------------------------------
    def SetSelected(self):
        self.bgcolor = BG_SELECTED
        self.mustRender = True

    #--------------------------------------------------------------------
    def SetUnSelected(self):
        self.bgcolor = BLACK
        self.mustRender = True

    #--------------------------------------------------------------------
    def loop(self):
        if self.speed and time.time() > self.keystart + DELAY:
            self.selected = self.selected + self.speed
            if( math.fabs(self.speed) < MAXSPEED) :
                self.speed *= ACCELERATION
            self.mustRender = True

#--------------------------------------------------------------------
