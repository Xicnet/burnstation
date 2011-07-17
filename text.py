import pygame
from pygame.locals import *

class TextSprite(pygame.sprite.Sprite):
    def __init__(self, group, string, size, x, y, color, bgcolor=(0,0,0), useBG=1):
        pygame.sprite.Sprite.__init__(self, group)

        self.string  = string
        self.size    = size
        self.x       = x
        self.y       = y 
        self.color   = color
        self.bgcolor = bgcolor
        self.useBG   = useBG

        self.Clear()

    def Clear(self):
        self.CreateSurface()

    def CreateSurface(self):
        self.image = pygame.Surface((self.x, self.y))
        self.image = self.image.convert()
        self.image.fill(self.bgcolor)
        self.rect = (self.x,self.y)
        #logger.debug("created surface text...")

    def UpdateText(self, string):
        self.string = string
        return self.Show()

    def SetColor(self, color):
        self.color = color
        return self.Show()

    def Show(self):
        #logger.debug("Displaying text: %s" % self.string)
        self.Clear()
        font = pygame.font.Font(None, self.size)
        text = font.render(self.string, 1, self.color)
        textpos = text.get_rect()
        textpos.x = 5 
        textpos.y = 5
        if self.useBG==1:
            self.image.blit(text, textpos)
            return self.image
        elif self.useBG==2:
            print "B"
            return text

class Text:
    def __init__(self, string, size, x, y, color, bgcolor=(0,0,0), useBG=1):
        self.string  = string
        self.size    = size
        self.x       = x
        self.y       = y 
        self.color   = color
        self.bgcolor = bgcolor
        self.useBG   = useBG

        self.Clear()

    def Clear(self):
        self.CreateSurface()

    def CreateSurface(self):
        self.bg = pygame.Surface((self.x, self.y))
        self.bg = self.bg.convert()
        self.bg.fill(self.bgcolor)
        #logger.debug("created surface text...")

    def UpdateText(self, string):
        self.string = string
        return self.Show()

    def SetColor(self, color):
        self.color = color
        return self.Show()

    def Show(self):
        #logger.debug("Displaying text: %s" % self.string)
        self.Clear()
        font = pygame.font.Font(None, self.size)
        text = font.render(self.string, 1, self.color)
        textpos = text.get_rect()
        textpos.x = 5 
        textpos.y = 5
        if self.useBG==1:
            self.bg.blit(text, textpos)
            return self.bg
        elif self.useBG==2:
            print "B"
            return text
