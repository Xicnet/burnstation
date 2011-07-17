#!/usr/bin/python
# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
import math
import time

import pygame
import pygame.joystick
import pygame.display

import os, os.path
from MiscTools import *
import urllib

RED=(200,0,0)
BLUE1=(10,20,50)
BG_SELECTED=(10,20,50)
ORANGE=(230,146,0)

from globals import * 

from text import Text 
from button import Button

import Socket
import shutil
import TextWidget
from Slider import Slider

from DriveSelector import *

import string

pygame.display.init()
pygame.joystick.init() #initialize joystick module
pygame.joystick.get_init() #verify initialization (boolean)

#--------------------------------------------------------------------
class Burner(pygame.sprite.Sprite):
    def __init__(self, group, parent_surface, posX, posY):
        logger.debug("starting burner")
        pygame.sprite.Sprite.__init__(self, group)

        self.group = group

        # Burner surface size
        self.image = pygame.Surface((500,300)).convert()
        self.image = self.image.convert()
        self.area  = self.image.get_rect()
        self.image.fill(BLUE1)

        self.rect = (400,900)

        self.parent_surface = parent_surface
        self.posX           = posX
        self.posY           = posY

        self.decodelog = config.logPath + "/decoder.log"
        if os.path.isfile(self.decodelog): os.unlink(self.decodelog)

        self.burnlog   = config.logPath + "/burn.log"
        if os.path.isfile(self.burnlog): os.unlink(self.burnlog)

        # render title
        title = Text("BURNING INFO", 28, 500, 35, RED).Show()
        self.image.blit(title, (0, 0))
        self.ShowHelp()

        self.mustRender = False
        self.Controls   = False
        self.Burning    = False
        self.BurnMode   = None
        self.Finished   = False

        self.visible  = False
        self.burning  = False
        self.decoding = False
        self.myclock  = None

        # make sure the temp (spool) dir is clean before we start
        self.Cleanup()
 
    #--------------------------------------------------------------------
    def Redraw(self, index=-1):
        self.items=[]
        for record in self.list:
            self.items.append(record['name'])
        self.getSelected(self.list, index)
        self.mustRender = True

    #--------------------------------------------------------------------
    def update(self):
        if self.mustRender or self.Controls or self.Burning or self.Finished:
            self.render()
            self.mustRender = False

    #--------------------------------------------------------------------
    def render(self):
        # burner background
        #self.image.fill(BLUE1)

        if self.Burning: self.ShowBurning()
        elif self.Finished: self.ShowFinished()
        else: pass #self.ShowProgress()
        self.ProgressBar(125, 125)

        #logger.debug( "rendered burner" )

    #--------------------------------------------------------------------
    def ShowClose(self):
        ######################################################
        # build play button text label
        t = Text("Press any key or button to EXIT  ", 24, 500, 55, ORANGE)
        close = t.Show()
        # render text at position
        self.image.blit(close, (0, 90))
        ######################################################

    #--------------------------------------------------------------------
    def ShowFinished(self):
        ######################################################
        # build play button text label
        if self.BurnMode == 'U':
            finished = "Finished copying !"
            removemedia = "Take your Pendrive and go enjoy!"
        else:
            finished = "Finished burning !"
            removemedia = "Take your CD and go enjoy!"

        t = Text(finished, 24, 500, 35, ORANGE)
        playlabel = t.Show()
        self.image.blit(playlabel, (0, 30))

        t = Text(removemedia, 24, 500, 35, ORANGE)
        playlabel = t.Show()
        self.image.blit(playlabel, (0, 60))
        ######################################################
        self.ShowClose()

    #--------------------------------------------------------------------
    def ShowHelp(self):
        """show burning help"""
        t = Text("Choose burning mode", 24, 500, 35, ORANGE)
        burninfo = t.Show()
        self.image.blit(burninfo, (0, 30))

        t = Text("<-- Options ", 24, 500, 35, ORANGE)
        burninfo = t.Show()
        self.image.blit(burninfo, (0, 60))

    #--------------------------------------------------------------------
    def ShowStarting(self, track_count):
        """show burning info"""
        t = Text("%i tracks to burn" % track_count, 24, 500, 35, ORANGE)
        burninfo = t.Show()
        self.image.blit(burninfo, (0, 30))

        if self.BurnMode == 'U':
            media = "Pendrive"
        else:
            media = "CD"

        label = "Burning your %s. Please, wait..." % media
        t = Text(label, 24, 500, 35, ORANGE)
        burninfo = t.Show()
        self.image.blit(burninfo, (0, 60))

    #--------------------------------------------------------------------
    def ShowBurning(self, status="burning.."):
        """show burning info"""

        t = Text(status, 24, 500, 35, ORANGE)
        burninfo = t.Show()
        self.image.blit(burninfo, (0, 90))
        ######################################################

    #--------------------------------------------------------------------
    def SetSelected(self):
        self.bgcolor = BG_SELECTED
        self.Controls = True
        self.mustRender = True

    #--------------------------------------------------------------------
    def SetUnSelected(self):
        self.bgcolor = BLACK
        self.mustRender = True

    #--------------------------------------------------------------------
    def GetStatus(self):
        if not self.decoding and not self.burning: return
        if self.decoding: self.GetDecodingStatus()
        elif self.burning: self.GetBurningStatus()

    #--------------------------------------------------------------------
    def GetDecodingStatus(self):
        try:
            log = open(self.decodelog)
            #logger.debug5("GetDecodingStatus() opened decode log: %s" % log)
            lines = log.readlines()
            lines_count = len(lines)
            try:
                line = lines[lines_count-1].strip()
                line_length = len(line)
                status = line
                if status == 'Decoding finished':
                    self.decoding = False
                    self.burning = True
                    os.unlink(self.decodelog)
                self.ShowBurning(status)
            except Exception, e:
                logger.warn("Impossible to read lines from decode log: %s" % str(e))
            log.close()
        except Exception, e:
            logger.warn("Decode log file not accessible: %s" % str(e))

    #--------------------------------------------------------------------
    def GetBurningStatus(self):
        if not self.burning or not os.path.isfile(self.burnlog): return
        log = open(self.burnlog)
        lines = log.readlines()
        lines_count = len(lines)
        amount = 64
        finished = False
        try:
            line = lines[lines_count-1].strip()
            line_length = len(line)
            status = line[line_length-amount:line_length]
            #logger.info(status)
            if self.BurnMode == 'U':
                UD = string.find(status, 'USB_DONE')
                logger.info("************** UD: %s" % UD)
                if string.find(status, 'USB_DONE') >= 0:
                    finished = True
                    status   = 'Finished copying! Please, take your pendrive and go.'
                    logger.debug("FINISHED USB")
            else:
                if string.find(status, 'Fixating time') >= 0:
                    finished = True
                    status   = 'Finished burning! Please, take your CD.'
            #if status == 'BURN-Free was never needed.' or finished == 0:
            if finished:
                self.burning = False
                self.Finished = True
            self.ShowBurning(status)
            if self.Finished:
                os.system("pumount /media/usburn")
                self.Cleanup()
                os.unlink(self.burnlog)
        except Exception, e:
            logger.warn("burning log file not accessible: %s" % str(e))
        """
        for line in lines:
            line_length = len(line)
            print line[line_length-amount:line_length][lines_count-10]
        """
        log.close()

    #--------------------------------------------------------------------
    def BurnCD(self, tracks, mode):
        # if there is no CD, do not start burning
        if mode == 'BURN_USB': mtype = 'Pendrive'
        else: mtype = 'CD-ROM'
        if not self.CheckMedia(mtype): return

        track_count = len( tracks.split(":") ) - 1

        if mode == 'BURN_AUDIO':
            mode = 'A'
            self.decoding = True
            self.BurnMode = 'A'
        elif mode == 'BURN_DATA' :
            mode = 'D'
            self.burning = True
            self.BurnMode = 'D'
        elif mode == 'BURN_USB' :
            print "Called burner to USB"
            mode = 'U'
            self.burning = True
            self.BurnMode = 'U'

        self.ShowStarting(track_count)

        message = "BURN_"+mode+"_123|||" + tracks
        Socket.socket_message(message)

    #--------------------------------------------------------------------
    def CheckMedia(self, mtype):
        try:
            ds = DriveSelector()
            drives = ds.drives
            media = False
            for drive in drives:
                if drive['mtype'] == mtype:
                    if drive['mtype'] == 'Pendrive':
                        print 'Detected pendrive'
                        print 'Mountpoint: ', drive['mountpoint']
                        print 'Is mounted: ', drive['is_mounted']
                        os.system("pmount %s usburn" % (drive['device']))
                        print 'Is mounted: ', drive['is_mounted']
                    media = True

            if media: return True
            else:
                status = "Please, insert a blank CD and try again!"
                os.system("eject")
                self.ShowBurning(status)
                return False
        except Exception, e: logger.error("burner EXCEPTION: " + str(e))


    #--------------------------------------------------------------------
    def CopyToUSB(self, tracks, playlistID):
        """Copy tracks to USB device"""

        device = "/media/PHILIPS"
        target = device + "/BurnStation-Playlist-%i" % playlistID

        os.mkdir(target)

        for track in tracks:
            logger.info("Copying %s to %s ..." % (track, target))
            shutil.copy(track, target)
        logger.info("Copy to USB finished!")

        """
        track_count = len( tracks.split(":") )
        self.ShowStarting(track_count)
        message = "BURN "+ tracks
        #message = "BURN A"
        Socket.socket_message(message)
        """

    #--------------------------------------------------------------------
    def Cleanup(self):
        temp_files = os.listdir(config.spoolPath)
        logger.debug("Found temp files: %s" % str(temp_files))
        for f in temp_files:
            file = config.spoolPath + f
            logger.debug("Removing file: %s" % file)
            try: os.unlink(file)
            except Exception, e: logger.error("EXCEPTION occurred while trying to cleanup spool dir: %s" % str(e))

    #--------------------------------------------------------------------
    def __BurnCD(self, tracks):
        '''Burn tracks'''

        burn_command = "python scripts/burn -A -a %s --eject" % tracks
        logger.debug("burn command: %s" % burn_command)

        # display a "now burning" label on top of the controls
        self.Burning = True
        self.render()
        pygame.display.flip()

        # start burning NOW !
        os.system(burn_command)
        self.Burning  = False
        self.Finished = True

    #--------------------------------------------------------------------
    def ToggleVisible(self):
        if self.Controls == True: return self.SetUnVisible()
        else: return self.SetVisible()

    #--------------------------------------------------------------------
    def SetVisible(self):
        logger.debug("***** SHOWING BURNER")
        self.rect = (400,20)
        self.SetSelected()
        self.visible = True

    #--------------------------------------------------------------------
    def SetUnVisible(self):
        logger.debug("***** NOT SHOWING BURNER")
        self.rect = (400,900)
        self.Controls   = False
        self.Burning    = False
        self.mustRender = False
        self.Finished   = False

        self.visible = False


    #--------------------------------------------------------------------
    def ProgressBar(self, x, y):
        """Playback position and seeking bar"""

        # size
        height = 10
        width  = 205

        # bar
        self.image.fill(BARDARK, self.image.get_rect(left=x, top=y, width=width, height=height))
        barheight = 10

        # cursor
        barrect = self.image.get_rect(left=x, width=10, height=barheight)
        barrect.top = y
        ratio = .9

        barrect.left = ((self.image.get_rect().width-barheight) * ratio / 2) + x
        self.image.fill(BARLIGHT, barrect)

    #--------------------------------------------------------------------
    def loop(self):
        if self.myclock == None:
            self.myclock = time.time()
        else:
            if ( time.time() - self.myclock ) > 1:
                 self.myclock = time.time()
                 self.GetStatus()
                 # reset clock
                 self.myclock = None

#--------------------------------------------------------------------
