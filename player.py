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

from globals import *

from text import Text 
from button import Button 

import Socket

pygame.display.init()
pygame.joystick.init() #initialize joystick module
pygame.joystick.get_init() #verify initialization (boolean)

#--------------------------------------------------------------------
class Player(pygame.sprite.Sprite):
    def __init__(self, group, parent_surface, posX, posY):
        pygame.sprite.Sprite.__init__(self, group)

        # Player surface size
        self.image = pygame.Surface((400,210))
        self.area = self.image.get_rect()
        self.parent_surface = parent_surface
        self.posX = posX
        self.posY = posY
        self.speed = 0
        self.volume = 0.5
        self.haveJoypad = pygame.joystick.get_count()
        self.haveJoypad = 1

        self.playtime = 100
        self.myclock = None
        self.playback_position = 0
        self.playing = False

        self.rect = self.image.get_rect()

        self.burnControls = False

        self.NowPlaying = "nothing"

        # Start with volume at half power
        try:
            pygame.mixer.music.set_volume(self.volume)
        except: logger.warn("sound sub-system not initialized")


        self.draw()

    #--------------------------------------------------------------------
    def draw(self):
        self.mustRender = True
        self.image.fill(BLACK)

        if self.haveJoypad:
            legend = Button(self.image, 285, 5, 'legende_small.png', '')
            JoyMap = load_image('controller_map.png')
            self.image.blit(JoyMap[0], (-30, 0))
        else:
            legend = Button(self.image, 285, 5, 'legende_small.png', '')
            self.JoyIcon = Button(self.image, 20, 15, 'keyboard.png', '')
            self.BtnPlay = Button(self.image, 20, 50, 'play.png', ' ->')
            self.BtnStop = Button(self.image, 70, 50, 'stop.png', '  x')
            self.BtnFwd  = Button(self.image, 120, 50, 'forward.png', ' c')
            self.BtnAdd  = Button(self.image, 170, 50,  'add.png', '  v' )
            self.BtnBurn = Button(self.image, 220, 50, 'burn.png', '  b')


        # volume display
        self.vol = Text("volume: ", 24, 100, 25, ORANGE, 2)
        #self.volumeter = self.vol.Show()

        self.SetVolume()


    #--------------------------------------------------------------------
    def stopMoving(self):
        self.speed = 0.0

    #--------------------------------------------------------------------
    def Play(self, filepath):
        '''Play the file'''
        self.playback_position = 0
        #if self.browser.level == 'jamendo': file = filepath
        #else: file = urllib.url2pathname(filepath)
        file = urllib.url2pathname(filepath)
        #file = "\\ ".join( p for p in file.split(" "))
        #logger.debug( "Play file : " + file )
        message = "PLAY " + file
        pygame.mixer.quit()
        Socket.socket_message(message)
        self.playing = True

    #--------------------------------------------------------------------
    def Stop(self):
        message = "STOP A"
        Socket.socket_message(message)
        self.SetNowPlaying("nothing")
        self.playing = False
        self.playback_position = 0
        self.mustRender = True

    #--------------------------------------------------------------------
    def update(self):
        if self.mustRender:
            self.render()
            self.mustRender = False

    #--------------------------------------------------------------------
    def render(self):
        #logger.debug("rendering player")

        self.image.blit(self.volumeter, (275, 0))
        self.track = Text("now playing: " + self.NowPlaying, 24, 570, 30, RED)

        x = 10
        y = 175
        self.image.blit(self.track.Show(), (x, y))
        self.SeekBar(x+5, y+25)

        #self.parent_surface.blit(self.image, (self.posX, self.posY))

    #--------------------------------------------------------------------
    def SetNowPlaying(self, trackInfo):
        self.NowPlaying = trackInfo
        self.render()

    #--------------------------------------------------------------------
    def ToggleBurnControls(self):
        if self.burnControls:
            # hide burning controls
            self.burnControls = False
            # redraw original player controls
            self.draw()
        else:
            # show burning controls
            self.ShowBurnControls()
            self.render()
            self.burnControls = True

    #--------------------------------------------------------------------
    def ShowBurnControls(self):
        #logger.debug("showing burn controls")
        if self.haveJoypad:
            self.image.fill((0,0,0))
            self.BurnMap = Button(self.image, -30, 0, 'controller_map.png', '')
            legend = Button(self.image, 285, 5, 'legende_small.png', '')
        else:
            self.image.fill((0,0,0))
            self.JoyIcon = Button(self.image, 20, 15, 'keyboard.png', '')
            self.BtnFwd  = Button(self.image, 120, 50, 'audio.png', '  1')
            self.BtnAdd  = Button(self.image, 170, 50,  'data.png', '  2')
            self.BtnUSB  = Button(self.image, 220, 50,  'usb.png', '  3')

    #--------------------------------------------------------------------
    def SetSelected(self):
        self.bgcolor = BG_SELECTED
        self.mustRender = True

    #--------------------------------------------------------------------
    def SetUnSelected(self):
        self.bgcolor = BLACK
        self.mustRender = True

    #--------------------------------------------------------------------
    def VolumeUp(self):
        self.ChangeVolume(1)

    #--------------------------------------------------------------------
    def ChangeVolume(self, direction):
        #logger.debug("self.volume = %f , MAXVOLUME = %f , MINVOLUME = %f" % (self.volume,MAXVOLUME,MINVOLUME))
        if direction == 1:
            if self.volume >= MAXVOLUME: return
        elif direction == -1:
            if self.volume <= MINVOLUME: return

        self.keystart = time.time()
        self.speed = 1.0 * direction

        self.volume = self.volume + self.speed / 10

        logger.info("Raising volume up to: %f" % self.volume)
        self.SetVolume()

    #--------------------------------------------------------------------
    def SetVolume(self):
        volume_label = int(self.volume * 10)
        self.volumeter = self.vol.UpdateText("volume: %1.0f" % (volume_label))
        self.mustRender = True

        message = "VOLU %f " % self.volume
        Socket.socket_message(message)

    #--------------------------------------------------------------------
    def VolumeDown(self):
        self.ChangeVolume(-1)

    #--------------------------------------------------------------------
    def loop(self):
        if self.volume >= MAXVOLUME or self.volume <= MINVOLUME: return

        # move volume level
        if self.speed and time.time() > self.keystart + DELAY:
            self.volume = self.volume + self.speed / 1000
            if( math.fabs(self.speed) < MAXSPEED) :
                self.speed *= ACCELERATION
            self.volumeter = self.vol.UpdateText("volume: %1.1f" % (self.volume))
            self.SetVolume()
            self.mustRender = True

        # move playback position bar
        if self.playing:
            if self.myclock == None:
                self.myclock = time.time()
            else:
                if ( time.time() - self.myclock ) > 1:
                    self.playback_position += 1
                    self.mustRender = True
                    self.myclock = None

    #--------------------------------------------------------------------
    def Seek(self, direction):
        seekSeconds = 10
        self.playback_position += seekSeconds
        message = "SEEK %i" % seekSeconds
        Socket.socket_message(message)
        self.mustRender = True

    #--------------------------------------------------------------------
    def SeekBar(self, x, y):
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

        if self.playing:
            if float(self.playback_position) <= float(self.playtime) + 1:
                ratio = float(self.playback_position) / float(self.playtime)
            else:
                logger.info("Playback ended!")
                self.playing = False
                ratio = 1.0
                self.Stop()
                PLAY_ENDED = pygame.event.Event(123)
                pygame.event.post(PLAY_ENDED)
        else:
            ratio = 0.0

        #logger.debug2("Playback position: %f/%f" % (self.playback_position, self.playtime))

        barrect.left = ((self.image.get_rect().width-barheight) * ratio / 2) + x
        self.image.fill(BARLIGHT, barrect)

    #--------------------------------------------------------------------
    def SetPlaytime(self, seconds):
        """Set track's lenth in seconds"""
        logger.debug2("Setting playtime to: %i" % seconds )
        if seconds < 1: seconds = 1;
        self.playtime = seconds

#--------------------------------------------------------------------
