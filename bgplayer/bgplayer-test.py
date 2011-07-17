#/usr/bin/env python
"""
burnstation - free media distribution system
"""

#Import Modules
import sys, os, pygame
from pygame.locals import *

import Common
import  LoadConfig
config = LoadConfig.LoadConfig()
basedir = config.bshome
sys.path.append(config.bshome)
Common.Init(config.bshome)

from player import Player
from MiscTools import *

if not pygame.font: logger.info('Warning, fonts disabled')
if not pygame.mixer: logger.info('Warning, sound disabled')

APP_NAME="Background player - burn station 2.0-beta"

SCREENWIDTH=1024
SCREENHEIGHT=768
STARTFULLSCREEN=0
BLACK=(0,0,0)
GREY=(100,100,100)
RED=(200, 10, 10)
RED1=(100, 10, 10)
RED2=(150, 10, 10)
RED3=(200, 10, 10)
RED4=(250, 10, 10)

ORANGE=(230,146,0)

burn=0


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

#---------------------------------------------------------------------------------
def main():
    """this function is called when the program starts.
       it initializes everything it needs, then runs in
       a loop until the function returns."""
#Initialize Everything
    pygame.init()
    screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    pygame.display.set_caption(APP_NAME)
    pygame.mouse.set_visible(1)

#Display The Background

    # UPDATE display
    #pygame.display.flip()

#Prepare Game Objects
    clock = pygame.time.Clock()

    # app title - init values: string, size, x, y, color
    #t = Text(APP_NAME, 36, 580, 40, RED)
    #title = t.Show()

    # player controls
    #t_pl = Text(APP_NAME, 32, 160, 38, RED)
    #title_pl = t_pl.UpdateText("Playlist #%i" % playlistID)
    player = Player(screen, 0, 25)

    # update all sprites
    allsprites = pygame.sprite.RenderPlain((player))

    if STARTFULLSCREEN: pygame.display.toggle_fullscreen()

#Main Loop
    while 1:
        clock.tick(60)

    #Handle Input Events
        for evt in pygame.event.get():
            if evt.type == QUIT:
                return
            elif evt.type == MOUSEBUTTONDOWN:
                mousepos = pygame.mouse.get_pos()
            elif evt.type is MOUSEBUTTONUP:
                #print "mouse button up"
                pass

                if evt.key == 27: # ESC
                    logger.info("Requested quit... come back soon, bye!")
                    return

        player.loop()

        allsprites.update()

    #Draw Everything

        #pygame.image.save(screen, "/tmp/bs2.0.png")

        #allsprites.draw(screen)
        pygame.display.flip()

#Game Over


#this calls the 'main' function when this script is executed
if __name__ == '__main__': main()


