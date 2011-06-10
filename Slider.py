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
class Slider(pygame.sprite.Sprite):
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
    def __init__(self, surface):
        pygame.sprite.Sprite.__init__(self)

        #self.w = w
        #self.h = h

        self.parent_surface = surface

        self.image = pygame.Surface((390,390))
        self.image = self.image.convert()
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()

        self.mustRender = True

    #--------------------------------------------------------------------
    def update(self):
        if self.mustRender:
            self.render()
            self.mustRender = False

    #--------------------------------------------------------------------
    def render(self):
        self.image.fill(WHITE)
        #logger.debug("rendering slider")

        self.image.fill(BARDARK, self.image.get_rect(left=10, width=10))
        barheight = 10
        barrect = self.image.get_rect(left=10, width=10, height=barheight)
        try: ratio = float(50) / len(100)
        except Exception, e: return
        barrect.top = (self.image.get_rect().height-barheight) * ratio
        self.image.fill(BARLIGHT, barrect)

        self.parent_surface.blit(self.image)
        pygame.display.flip()

#--------------------------------------------------------------------
