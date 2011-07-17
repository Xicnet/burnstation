#!/BIn/env python
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

from text import Text 

pygame.display.init()
pygame.joystick.init() #initialize joystick module
pygame.joystick.get_init() #verify initialization (boolean)

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', fullname
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
class Button(pygame.sprite.Sprite):
    def __init__(self, parent_surface, posX, posY, image, label):
        pygame.sprite.Sprite.__init__(self)

        # load button image
        self.image, self.rect = load_image(image, -1)

        # Player surface size
        self.surface = pygame.Surface((self.rect.width, self.rect.height+40))
        self.area = self.surface.get_rect()

        self.parent_surface = parent_surface
        self.posX  = posX
        self.posY  = posY
        self.label = label

        self.mustRender = True
        self.render()

    #--------------------------------------------------------------------
    def update(self):
        if self.mustRender:
            self.render()
            self.mustRender = False

    #--------------------------------------------------------------------
    def SetLabel(self):
        font = pygame.font.Font(None, 28)
        text = font.render(self.label, 1, RED)
        textpos = text.get_rect()
        textpos.x = 0
        textpos.y = 0
        self.surface.blit(text, (0, self.rect.height+10))

    #--------------------------------------------------------------------
    def render(self):
        # player background
        #self.surface.fill(BLUE1)

        ######################################################
        # build burn button text label
        # burn button image
        self.button = self.surface.blit(self.image, (0, 0))
        # place a text label
        self.SetLabel()
        ######################################################

        self.parent_surface.blit(self.surface, (self.posX, self.posY))

        #logger.debug( "rendered button" )

#--------------------------------------------------------------------
