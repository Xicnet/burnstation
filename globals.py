
WIDTH=1024
HEIGHT=768
SCREENWIDTH=1024
SCREENHEIGHT=768

FRAMERATE=30
VISIBLES=15
FONTSIZE=60

DELAY=.25
ACCELERATION=1.05
MAXSPEED=10
MAXVOLUME=1.000000
MINVOLUME=0.000000

BLACK=(0,0,0)
WHITE=(255,255,255)
GREY=(100,100,100)
#RED=(200,0,0)
RED=(200, 10, 10)
RED1=(100, 10, 10)
RED2=(150, 10, 10)
RED3=(200, 10, 10)
RED4=(250, 10, 10)
ORANGE=(230,146,0)
ORANGE=(200,50,0)
BLUE1=(10,20,50)
BG_SELECTED=(64,16,0)

ORANGENESS=.7
BARLIGHT=(255,255*ORANGENESS,0)
BARDARK=(128,128*ORANGENESS,0)

import pygame
from pygame.locals import *
import os

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

