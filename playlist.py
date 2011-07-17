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
from Browser import *
from text import *

import sys
sys.path.append("publish/")
from publisher import Publisher

pygame.display.init()
pygame.joystick.init() #initialize joystick module
pygame.joystick.get_init() #verify initialization (boolean)

from globals import *

#--------------------------------------------------------------------
class Playlist(pygame.sprite.Sprite):
    """
    The playlist sprite
    """
    def __init__(self, group, type):
        pygame.sprite.Sprite.__init__(self, group)

        self.group = group

        self.isSelected = False

        self.speed      = 0
        self.keystart   = 0

        self.image = pygame.Surface((600,50))
        self.image = self.image.convert()
        #self.image.fill((0,0,0))

        self.mustRender = True

        if type == 'path': self.type = 'fs_playlist'
        else: self.type = 'playlist'

        self.OpenPlaylist(self.type)

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
    def SetType(self, type):
        if self.type == 'playlist': self.type = 'fs_playlist'
        elif self.type == 'fs_playlist': self.type = 'playlist'

        #logger.debug5( self.type )
        #logger.debug5( self.browser.level )
        #logger.debug5( self.browser.browser.level )

        self.level = self.type
        self.browser.BrowserInit(self.level)
        self.browser.level = self.type
        self.browser.browser.level = self.type


    #--------------------------------------------------------------------
    def OpenPlaylist(self, level):
        """Open playlist with self.playlistID"""

        self.playlistID = playlistID = Database.CreatePlaylist()
        logger.info("Created new playlist ID = %i" % playlistID)
        #self.playlistID = playlistID = 26
        #self.playlistID = playlistID = 444
        #self.playlistID = playlistID = 1170

        #if self.level == 'path': level = 'fs_playlist'
        self.browser = Scroller(self.group, Browser(level, self.playlistID), self.image, 30, BLACK, 28, 20, 500,200)
        if self.isSelected: self.SetSelected()
        self.browser.level = self.browser.browser.level
        self.browser.rect = (500,0)

        self.t_pl = TextSprite(self.group, "Playlist..........", 32, 520, 30, RED)
        self.title = self.t_pl.UpdateText("Playlist #%i" % self.playlistID)
        self.browser.Refresh()
        #self.render()
        logger.info("Playlist #%i opened!" % self.playlistID)

    #--------------------------------------------------------------------
    def Publish(self, user, label):
        Database.PublishPlaylist(self.playlistID, user, label)

    #--------------------------------------------------------------------
    def ChangePlaylist(self, color):
        self.title = self.t_pl.SetColor(color)

    #--------------------------------------------------------------------
    def Refresh(self):
        self.list = self.browser.list
        self.browser.Refresh()
        self.render()

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
        self.speed    = 0.0
        self.playlistID = int(round(self.playlistID))
        self.render()

    #--------------------------------------------------------------------
    def previous(self):
        """Move to previous playlist by ID"""

        self.keystart    = time.time()
        self.playlistID -= 1
        self.speed       = -1.0
        self.OpenPlaylist()
        self.render()

    #--------------------------------------------------------------------
    def next(self):
        """Move to next playlist by ID"""

        self.keystart    = time.time()
        self.playlistID += 1
        self.speed       = 1.0
        self.OpenPlaylist()
        self.render()

    #--------------------------------------------------------------------
    def BrowseForward(self):
        self.browser.BrowseForward()
 
    #--------------------------------------------------------------------
    def BrowseBack(self):
        self.browser.BrowseBack()
 
    #--------------------------------------------------------------------
    def AddToRemoveFromPlaylist(self, playlistID):
        self.browser.AddToRemoveFromPlaylist(self.playlistID)
        self.browser.Refresh()
        self.render()

    #--------------------------------------------------------------------
    def Next(self):
        print self.list[self.selected+1]['location']

    #--------------------------------------------------------------------
    def update(self):
        if self.mustRender:
            self.render()
            self.mustRender = False

    #--------------------------------------------------------------------
    def render(self):
        #self.image.fill(WHITE)
        self.selected = self.browser.selected

        # render the playlist browser sprite
        self.browser.render()

        # Set playlist title including playlist ID
        self.image.blit(self.title, (20, 0))

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
    def loop(self):
        self.browser.loop()

        if self.speed and time.time() > self.keystart + DELAY:
            self.playlistID = self.playlistID + self.speed
            if( math.fabs(self.speed) < MAXSPEED) :
                self.speed *= ACCELERATION
            self.OpenPlaylist()
            self.render()


#--------------------------------------------------------------------
