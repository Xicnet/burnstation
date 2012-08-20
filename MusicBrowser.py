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

from scroller import Scroller
from textbox import Textbox
from Browser import *
#from Infopanel import *
from text import *

pygame.display.init()
pygame.joystick.init() #initialize joystick module
pygame.joystick.get_init() #verify initialization (boolean)

from globals import *

#--------------------------------------------------------------------
class MusicBrowser(pygame.sprite.Sprite):
    """
    The music browser sprite
    """
    def __init__(self, group, type):
        pygame.sprite.Sprite.__init__(self, group)

        self.group = group
        self.infotext = []

        self.isSelected = False

        self.speed      = 0
        self.keystart   = 0

        self.image = pygame.Surface((300,300))
        self.image = self.image.convert()
        #self.image.fill((0,100,100))
        self.rect = (0,250)

        self.mustRender = True

        if type == 'path': self.level = 'path'
        elif type == '': self.level = 'labels'
        elif type == 'labels': self.level = 'labels'
        else: self.level = 'labels'

        self.type = type

        self.BrowserInit()
        #self.InfopanelInit()

        self.la = Text("", 28, 570, 50, ORANGE)
        self.ar = Text("", 28, 570, 50, ORANGE)
        self.al = Text("", 28, 570, 50, ORANGE)
        #self.tr = Text("", 28, 570, 50, ORANGE)

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
        self.action[118] = self.AddToRemoveFromPlaylist

    #--------------------------------------------------------------------
    def BrowserInit(self):
        self.browser = Scroller(self.group, Browser(self.level), self.image, 30, BLACK, 36, 15, 400,300)
        self.browser.level = self.browser.browser.level

        self.browser.rect = (300,350)
        if self.isSelected: self.SetSelected()

        #self.browser.Refresh()

    #--------------------------------------------------------------------
    #def InfopanelInit(self):
    #    self.infopanel = Textbox(self.group, self.infotext, self.image, 10, 30, WHITE, 36, 15, 400,300, False)

    #    self.infopanel.rect = (700,350)

        #self.browser.Refresh()

    #--------------------------------------------------------------------
    def SetType(self, type):
        if self.type == 'labels': self.type = 'path'
        elif self.type == 'path': self.type = 'labels'

        #logger.debug5( self.type )
        #logger.debug5( self.browser.level )
        #logger.debug5( self.browser.browser.level )

        self.level = self.type
        self.browser.BrowserInit(self.level)
        #self.infopanel.BrowserInit([])
        self.browser.level = self.type
        self.browser.browser.level = self.type

        self.SetLabel("")
        self.SetArtist("")
        self.SetAlbum("")
        self.Refresh()

    #--------------------------------------------------------------------
    def Refresh(self):
        self.list = self.browser.list
        self.browser.Refresh()
        #self.infopanel.BrowserInit([{'name':'otro'}])
        #self.infopanel.Refresh()
        self.mustRender = True

    #--------------------------------------------------------------------
    def goUp(self):
        self.browser.goUp()
        self.mustRender = True

    #--------------------------------------------------------------------
    def goDown(self):
        self.browser.goDown()
        self.mustRender = True

    #--------------------------------------------------------------------
    def stopMoving(self):
        self.browser.stopMoving()

    #--------------------------------------------------------------------
    def BrowseForward(self):
        name = self.browser.list[self.browser.selected]['name']
        if self.browser.browser.level == 'artists': self.SetLabel(name)
        elif self.browser.browser.level == 'albums': self.SetArtist(name)
        elif self.browser.browser.level == 'tracks': self.SetAlbum(name)
        self.mustRender = True
        self.browser.BrowseForward()
 
    #--------------------------------------------------------------------
    def BrowseBack(self):
        self.browser.BrowseBack()
        if self.browser.browser.level == 'artists': self.SetLabel("")
        elif self.browser.browser.level == 'albums': self.SetArtist("")
        elif self.browser.browser.level == 'tracks': self.SetAlbum("")
        self.mustRender = True
 
    #--------------------------------------------------------------------
    def AddToRemoveFromPlaylist(self, playlistID):
        self.browser.AddToRemoveFromPlaylist(playlistID)

    #--------------------------------------------------------------------
    def Next(self):
        print self.list[self.selected+1]['location']

    #--------------------------------------------------------------------
    def update(self):
        if self.mustRender:
            #self.infopanel.SetText(self.browser.list[self.browser.selected]['info'])
            #self.infopanel.mustRender = True
            #self.infopanel.Refresh()
            self.render()
            self.mustRender = False

    #--------------------------------------------------------------------
    def render(self):
        self.image.fill(BLACK)
        self.selected = self.browser.selected

        # render the browser sprite
        #self.browser.mustRender = True

        self.navigation()
        self.browser.update()
        #self.infopanel.update()
        self.showRelatedImage((60,100), self.image)
        #logger.debug5( "self.level: " + self.level)

    #--------------------------------------------------------------------
    def showRelatedImage(self, pos, image):
        # show related image
        itemImg = ''
        if type(self.selected) is int:
            try: itemImg = self.browser.list[self.selected]['img']
            except Exception, e: logger.error("MusicBrowser EXCEPTION: %s" % str(e) )
            if itemImg != '':
                imgsrc = ValidateImage(itemImg, self.browser.level)
                if imgsrc:
                    #logger.debug( "loading image: " + imgsrc )
                    self.showImage(imgsrc, pos, self.image)
                else: return True
        else: return False

    #--------------------------------------------------------------------
    def showImage(self, imgfile, pos, image):
        #self.image, self.rect = load_image(imgfile, -1)
        #self.image.blit(self.image, pos)
        img = pygame.image.load(imgfile)
        #frame = pygame.image.load('data/frame.png').convert_alpha()
        #img.blit(frame, (-22, -12))
        self.image.blit(img, pos)


    #--------------------------------------------------------------------
    def navigation(self):
        """Display navigation position"""

        self.image.blit(self.la.Show(), (0, 0))

        self.image.blit(self.ar.Show(), (10, 30))

        self.image.blit(self.al.Show(), (20, 60))

        #self.image.blit(self.tr.Show(), (400, 85))

    #--------------------------------------------------------------------
    def SetLabel(self, s):
        if s == "": tag = ""
        else: tag = "Label   : "
        self.la.UpdateText(tag + s)

    #--------------------------------------------------------------------
    def SetArtist(self, s):
        if s == "": tag = ""
        else: tag = "Artist   : "
        self.ar.UpdateText(tag + s)

    #--------------------------------------------------------------------
    def SetAlbum(self, s):
        if s == "": tag = ""
        else: tag = "Album : "
        self.al.UpdateText(tag + s)

    #--------------------------------------------------------------------
    def SetFocus(self, state):
        if state: self.SetSelected()
        else: self.SetUnSelected()

    #--------------------------------------------------------------------
    def SetSelected(self):
        self.browser.SetSelected()
        self.isSelected = True

    #--------------------------------------------------------------------
    def SetUnSelected(self):
        self.browser.SetUnSelected()
        self.isSelected = False
        self.render()

    #--------------------------------------------------------------------
    def SetVisible(self):
        self.browser.rect = (400,350)
        #self.browser.mustRender()

    #--------------------------------------------------------------------
    def SetUnVisible(self):
        self.browser.rect = (400,900)

    #--------------------------------------------------------------------
    def loop(self):
        self.browser.loop()
        #self.infopanel.loop()


#--------------------------------------------------------------------
