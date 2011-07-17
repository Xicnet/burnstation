# by Timothy Downs, inputbox written for my map editor

# This program needs a little cleaning up
# It ignores the shift key
# And, for reasons of my own, this program converts "-" to "_"

# A program to get user input, allowing backspace etc
# shown in a box in the middle of the screen
# Called by:
# import inputbox
# answer = inputbox.ask(screen, "Your name")
#
# Only near the center of the screen is blitted to

import pygame, pygame.font, pygame.event, pygame.draw, string
from pygame.locals import *
from globals import *

from MiscTools import *

import time

from text import * 

#--------------------------------------------------------------------
class Form(pygame.sprite.Sprite):
    """A simple form sprite"""
    #--------------------------------------------------------------------
    def __init__(self, group):
        pygame.sprite.Sprite.__init__(self, group)

        self.mustRender = True
        self.group = group

        # surface size
        self.image = pygame.Surface((500,180)).convert()
        self.image = self.image.convert()
        self.image.fill((0,60,0))
        self.rect = (300,900)
        self.visible = False

        self.Start()

        self.SetError("--------------")

    #--------------------------------------------------------------------
    def Start(self):
        self.finished = False
        self.current_field = 0
        self.key = None
        self.results = {}

    #--------------------------------------------------------------------
    def Restart(self):
        self.Start()
        for i in range(0, len(self.fields)):
            self.fields[i].get_input = True
            self.fields[i].current_string = []

    #--------------------------------------------------------------------
    def SetTitle(self, title):
        """Set title string"""
        self.title = Text(title, 34, 150, 35, RED)

    #--------------------------------------------------------------------
    def SetError(self, error):
        """Set error string"""
        self.error = Text(error, 24, 250, 35, RED)

    #--------------------------------------------------------------------
    def SetFields(self, fields=None):
        x = 10
        y = 50

        self.fields = []

        for field in fields:
            y += 30
            self.fields.append( InputBox(self.group, field, self.image, (x, y)) )

        self.current_field = 0

    #--------------------------------------------------------------------
    def get_user_input(self, key):
        """Read user input"""

        self.mustRender = True
        if self.fields[self.current_field].get_input:
            self.fields[self.current_field].get_key(key)
        else:
            if self.current_field < len(self.fields)-1:
                self.current_field += 1
                self.fields[self.current_field].get_key(key)
            else:
                for i in range(0, len(self.fields)):
                    logger.info( str(self.fields[i].result) )
                self.finished = True
                self.mustRender = False
        self.key = None


    #--------------------------------------------------------------------
    def FormError(self, s):
        logger.error("Form result: " + s)
        self.error.UpdateText(s)
        self.render()

    #--------------------------------------------------------------------
    def update(self):
        if self.finished: return
        self.get_user_input(self.key)
        if self.mustRender:
            self.render()
            self.mustRender = False

    #--------------------------------------------------------------------
    def render(self):
        self.fields[0].surface.fill((0,30,30))
        self.image.blit(self.title.Show(), (0, 0))
        self.image.blit(self.error.Show(), (0, 30))
        for i in range(0, len(self.fields)):
            self.fields[i].mustRender = True
            self.fields[i].update()

    #--------------------------------------------------------------------
    def SetFocus(self, state):
        self.isFocused = state

    #--------------------------------------------------------------------
    def ToggleVisible(self):
        if self.visible: return self.SetUnVisible()
        else: return self.SetVisible()

    #--------------------------------------------------------------------
    def SetVisible(self):
        logger.debug5("SetVisible form sprite")
        self.rect = (400,350)
        self.visible = True
        self.mustRender = True

    #--------------------------------------------------------------------
    def SetUnVisible(self):
        logger.debug5("SetUnVisible form sprite")
        self.rect = (300,900)
        self.mustRender = False
        self.visible = False



#--------------------------------------------------------------------
class InputBox(pygame.sprite.Sprite):
    """..."""
    #--------------------------------------------------------------------
    def __init__(self, group, label, surface, pos):
        pygame.sprite.Sprite.__init__(self)

        self.surface = surface
        self.rect = self.pos = (pos[0],pos[1])
        self.pos2 = (pos[0]+60,pos[1]-5)

        self.get_input = True
        self.inkey = None
        self.current_string = []
        self.label = label

        self.get_key(None)
        self.results = {}
        self.result = ""

    #--------------------------------------------------------------------
    def update(self):
        if self.mustRender:
            self.render()
            self.mustRender = False

    #--------------------------------------------------------------------
    def render(self):
        self.image = self.display_box(self.label + "    " + string.join(self.current_string,""))
        self.surface.blit(self.image, (self.pos))

    #--------------------------------------------------------------------
    def get_key(self, key):
      """Ask and get input keys"""
      self.inkey = key
      input_data = self.ask(self.label, key)
      if not self.get_input:
        if input_data is not "":
          if type(input_data) is str:
              #logger.info( self.label + " : " + str(input_data) )
              self.result = input_data
              pass
          #self.current_string = ""
    
    #--------------------------------------------------------------------
    def display_box(self, message):
      "Print a message in a box in the middle of the screen"
      fontobject = pygame.font.Font(None,18)
      pygame.draw.rect(self.surface, (0,0,10),
                       (self.pos2[0],
                        self.pos2[1],
                        200,20), 0)
      pygame.draw.rect(self.surface, (255,255,25),
                       (self.pos2[0],
                        self.pos2[1],
                        204,24), 1)
      if len(message) != 0:
          self.mustRender = True
          return  fontobject.render(message, 1, (255,255,255))
    
    #--------------------------------------------------------------------
    def ask(self, label, inkey):
      "ask(screen, label) -> answer"
      if not self.get_input: return self.current_string
      if self.current_string is not "": self.display_box(label + ": " + string.join(self.current_string,""))
      if inkey is not None:
        if inkey == K_ESCAPE:
            pass #self.current_string.append("AA")
        elif inkey == K_BACKSPACE:
          self.current_string = self.current_string[0:-1]
        elif inkey == K_RETURN:
          self.get_input = False
          return string.join(self.current_string,"")
        elif inkey == K_MINUS:
          self.current_string.append("_")
        elif inkey <= 127:
          if inkey is not None:
            self.mustRender = True
            self.current_string.append(chr(inkey))
        else: pass

      return string.join(self.current_string,"")
    
#--------------------------------------------------------------------
