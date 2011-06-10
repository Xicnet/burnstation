
import sys
import time

import pygame
import pygame.joystick
import pygame.display

pygame.display.init()
pygame.joystick.init() #initialize joystick module
pygame.joystick.get_init() #verify initialization (boolean)

BUTTON_X = "but X"
BUTTON_Y = "but Y"

# initialize
num_joysticks = pygame.joystick.get_count()
if num_joysticks > 0:
    stick = pygame.joystick.Joystick(0)
    stick.init() # now we will receive events for the joystick
    axes = pygame.joystick.Joystick(0).get_numaxes()
    hats = pygame.joystick.Joystick(0).get_numhats()

print "Joysticks: %i" % num_joysticks
print "Axes: %i" % axes
print "Hats: %i" % hats
print "pygame.JOYAXISMOTION = %i" % pygame.JOYAXISMOTION

#sys.exit(0)

# event loop
while 1:
    for event in pygame.event.get():
        #if event.axis != 4:
	if 0: print "event IS: %s" % str(event)

    event = pygame.event.poll()

    if event.type is not 0: print event.type

    
    for a in range(axes):
        v = pygame.joystick.Joystick(0).get_axis(a)
        if v <> 0: print "AXIS %i: %f" % (a,v)

  #  if event.type != 0:
    if True:
        # print full event info

        if event.type == pygame.JOYBUTTONDOWN:
            joy = event.joy
            butt = event.button
            print "Joy: %i Button: %i DOWN" % (joy,butt)
 #       if event.type == pygame.JOYAXISMOTION:
            joy = event.joy
            axis = event.axis
            print "Joy: %i Axis: %i = $i" % (joy,axis,pygame.joystick.Joystick(0).get_axis(0))

    time.sleep(0.5)
