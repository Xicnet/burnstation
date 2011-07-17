"""

    (C) Copyright 2007 Anthony Maro

   Version 1.0.1 - September 5th, 2007
       
   This program is free software; you can redistribute it and/or
   modify it under the terms of the GNU General Public License as
   published by the Free Software Foundation; either version 2 of the
   License, or (at your option) any later version.

   This program is distributed in the hope that it will be useful, but
   WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
   General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
   02111-1307, USA.
 
   
   Usage:
   
   import virtkeyboard
   
   mykeys = virtkeyboard.VirtualKeyboard()
   userinput = mykeyboard.run(screen, default_text)
   
   screen is a full screen pygame screen.  The VirtualKeyboard will shade out the current screen and overlay
   a transparent keyboard.  default_text gets fed to the initial text import - used for editing text fields
   If the user clicks the escape hardware button, the default_text is returned
   
   
"""
import pygame, time, gtk
from pygame.locals import *

class TextInput(object):
    ''' Handles the text input box and manages the cursor '''
    def __init__(self, background, screen, text, x, y):
        self.x = x
        self.y = y
        self.text = text
        self.width = 800
        self.height = 60        
        self.font = pygame.font.Font(None, 50)
        self.cursorpos = len(text)
        self.rect = Rect(self.x,self.y,self.width,self.height)
        self.layer = pygame.Surface((self.width,self.height),SRCALPHA).convert_alpha()
        self.background = pygame.Surface((self.width,self.height),SRCALPHA).convert_alpha()
        self.background.blit(background,(0,0),self.rect) # Store our portion of the background
        self.cursorlayer = pygame.Surface((3,50))
        self.screen = screen
        self.cursorvis = True
        
        self.draw()
    
    def draw(self):
        ''' Draw the text input box '''
        self.layer.fill([255, 255, 255, 140])
        color = [0,0,0,200]
        pygame.draw.rect(self.layer, color, (0,0,self.width,self.height), 1)        
        
        text = self.font.render(self.text, 1, (0, 0, 0))
        self.layer.blit(text,(4,4))               
        
        self.screen.blit(self.background,(self.x, self.y))
        self.screen.blit(self.layer,(self.x,self.y))        
        self.drawcursor()
    
    def flashcursor(self):
        ''' Toggle visibility of the cursor '''
        if self.cursorvis:
            self.cursorvis = False
        else:
            self.cursorvis = True
        
        self.screen.blit(self.background,(self.x, self.y))
        self.screen.blit(self.layer,(self.x,self.y))  
        
        if self.cursorvis:
            self.drawcursor()
        pygame.display.flip()
        
    def addcharatcursor(self, letter):
        ''' Add a character whereever the cursor is currently located '''
        if self.cursorpos < len(self.text):
            # Inserting in the middle
            self.text = self.text[:self.cursorpos] + letter + self.text[self.cursorpos:]
            self.cursorpos += 1
            self.draw()
            return
        self.text += letter
        self.cursorpos += 1
        self.draw()   
        
    def backspace(self):
        ''' Delete a character before the cursor position '''
        if self.cursorpos == 0: return
        self.text = self.text[:self.cursorpos-1] + self.text[self.cursorpos:]
        self.cursorpos -= 1
        self.draw()
        return

        
    def deccursor(self):
        ''' Move the cursor one space left '''
        if self.cursorpos == 0: return
        self.cursorpos -= 1
        self.draw()
        
    def inccursor(self):
        ''' Move the cursor one space right (but not beyond the end of the text) '''
        if self.cursorpos == len(self.text): return
        self.cursorpos += 1
        self.draw()
        
    def drawcursor(self):
        ''' Draw the cursor '''
        x = 4
        y = 5 + self.y
        # Calc width of text to this point
        if self.cursorpos > 0:
            mytext = self.text[:self.cursorpos]
            text = self.font.render(mytext, 1, (0, 0, 0))
            textpos = text.get_rect()
            x = x + textpos.width + 1
        self.screen.blit(self.cursorlayer,(x,y))    
        

class VirtualKey(object):
    ''' A single key for the VirtualKeyboard '''
    def __init__(self, caption, x, y, w=67, h=67):
        self.x = x
        self.y = y
        self.caption = caption
        self.width = w
        self.height = h
        self.enter = False
        self.bskey = False
        self.font = None
        self.selected = False
        self.dirty = True
        self.keylayer = pygame.Surface((self.width,self.height)).convert()
        self.keylayer.fill((0, 0, 0))
        self.keylayer.set_alpha(160)
        # Pre draw the border and store in my layer
        pygame.draw.rect(self.keylayer, (255,255,255), (0,0,self.width,self.height), 1)
        
    def draw(self, screen, background, shifted=False, forcedraw=False):
        '''  Draw one key if it needs redrawing '''
        if not forcedraw:
            if not self.dirty: return
        
        myletter = self.caption
        if shifted:
            if myletter == 'SHIFT':
                self.selected = True # Draw me uppercase
            myletter = myletter.upper()
        
        
        position = Rect(self.x, self.y, self.width, self.height)
        
        # put the background back on the screen so we can shade properly
        screen.blit(background, (self.x,self.y), position)      
        
        # Put the shaded key background into my layer
        if self.selected: 
            color = (200,200,200)
        else:
            color = (0,0,0)
        
        # Copy my layer onto the screen using Alpha so you can see through it
        pygame.draw.rect(self.keylayer, color, (1,1,self.width-2,self.height-2))                
        screen.blit(self.keylayer,(self.x,self.y))    
                
        # Create a new temporary layer for the key contents
        # This might be sped up by pre-creating both selected and unselected layers when
        # the key is created, but the speed seems fine unless you're drawing every key at once
        templayer = pygame.Surface((self.width,self.height))
        templayer.set_colorkey((0,0,0))
                       
        color = (255,255,255)
        if self.bskey:
            pygame.draw.line(templayer, color, (52,31), (15,31),2)
            pygame.draw.line(templayer, color, (15,31), (20,26),2)
            pygame.draw.line(templayer, color, (15,32), (20,37),2)
        elif self.enter:
            pygame.draw.line(templayer, color, (100,21), (100,31),2)
            pygame.draw.line(templayer, color, (100,31), (25,31),2)
            pygame.draw.line(templayer, color, (25,31), (30,26),2)
            pygame.draw.line(templayer, color, (25,32), (30,37),2)
            
        else:
            text = self.font.render(myletter, 1, (255, 255, 255))
            textpos = text.get_rect()
            blockoffx = (self.width / 2)
            blockoffy = (self.height / 2)
            offsetx = blockoffx - (textpos.width / 2)
            offsety = blockoffy - (textpos.height / 2)
            templayer.blit(text,(offsetx, offsety))
        
        screen.blit(templayer, (self.x,self.y))
        self.dirty = False

class VirtualKeyboard(object):
    ''' Implement a basic full screen virtual keyboard for touchscreens '''
    def run(self, screen, text=''):
        # First, make a backup of the screen        
        self.screen = screen
        self.background = pygame.Surface((800,480))        
        
        # Copy original screen to self.background
        self.background.blit(screen,(0,0))
        
        # Shade the background surrounding the keys
        self.keylayer = pygame.Surface((800,480))
        self.keylayer.fill((0, 0, 0))
        self.keylayer.set_alpha(100)
        self.screen.blit(self.keylayer,(0,0))
        
        self.keys = []
        self.textbox = pygame.Surface((800,30))
        self.text = text
        self.caps = False
        
        pygame.font.init() # Just in case 
        self.font = pygame.font.Font(None, 40)   
        
        self.input = TextInput(self.background,self.screen,self.text,0,30)
        
        self.addkeys()
          
        self.paintkeys()
        counter = 0
        # My main event loop (hog all processes since we're on top, but someone might want
        # to rewrite this to be more event based.  Personally it works fine for my purposes ;-)
        while 1:
            time.sleep(.05)
            events = pygame.event.get() 
            if events <> None:
                for e in events:
                    if (e.type == KEYDOWN):
                        if e.key == K_ESCAPE:
                            self.clear()
                            return self.text # Return what we started with
                        if e.key == K_RETURN:
                            self.clear()
                            return self.input.text # Return what the user entered
                        if e.key == K_LEFT:
                            self.input.deccursor()
                            pygame.display.flip()
                        if e.key == K_RIGHT:
                            self.input.inccursor()
                            pygame.display.flip()
                    if (e.type == MOUSEBUTTONDOWN):
                        self.selectatmouse()   
                    if (e.type == MOUSEBUTTONUP):
                        if self.clickatmouse():
                            # user clicked enter if returns True
                            self.clear()
                            return self.input.text # Return what the user entered
                    if (e.type == MOUSEMOTION):
                        if e.buttons[0] == 1:
                            # user click-dragged to a different key?
                            self.selectatmouse()
                        
            counter += 1
            if counter > 10:                
                self.input.flashcursor()
                counter = 0
            gtk.main_iteration(block=False)
        
    def unselectall(self, force = False):
        ''' Force all the keys to be unselected
            Marks any that change as dirty to redraw '''
        for key in self.keys:
            if key.selected:
                key.selected = False
                key.dirty = True
    
    def clickatmouse(self):
        ''' Check to see if the user is pressing down on a key and draw it selected '''
        self.unselectall()
        for key in self.keys:
            myrect = Rect(key.x,key.y,key.width,key.height)
            if myrect.collidepoint(pygame.mouse.get_pos()):
                key.dirty = True
                if key.bskey:
                    # Backspace
                    self.input.backspace()
                    self.paintkeys() 
                    return False
                if key.caption == 'SPACE':                    
                    self.input.addcharatcursor(' ')
                    self.paintkeys() 
                    return False
                if key.caption == 'SHIFT':
                    self.togglecaps()
                    self.paintkeys() 
                    return False
                if key.enter:
                    return True
                    
                mykey = key.caption
                if self.caps:
                    mykey = mykey.upper()
                self.input.addcharatcursor(mykey)
                self.paintkeys()
                return False
            
        self.paintkeys() 
        return False
        
    def togglecaps(self):
        ''' Toggle uppercase / lowercase '''
        if self.caps: 
            self.caps = False
        else:
            self.caps = True
        for key in self.keys:
            key.dirty = True        
        
    def selectatmouse(self):
        ''' User has clicked a key, let's use it '''
        self.unselectall()
        for key in self.keys:
            myrect = Rect(key.x,key.y,key.width,key.height)
            if myrect.collidepoint(pygame.mouse.get_pos()):
                key.selected = True
                key.dirty = True
                self.paintkeys()
                return
            
        self.paintkeys()        
            
    def addkeys(self):
        ''' Adds the setup for the keys.  This would be easy to modify for additional keys
        
         The default start position places the keyboard slightly left of center by design
         so many people have issues with the right side of their touchscreens that I did this
         on purpose. '''
        
        x = 10 
        y = 140
        
        row = ['1','2','3','4','5','6','7','8','9','0']
        for item in row:
            onekey = VirtualKey(item,x,y)
            onekey.font = self.font
            self.keys.append(onekey)
            x += 70
            
        onekey = VirtualKey('<-',x,y)
        onekey.font = self.font
        onekey.bskey = True
        self.keys.append(onekey)
        
        y += 70
        x = 10
        
        row = ['q','w','e','r','t','y','u','i','o','p']
        for item in row:
            onekey = VirtualKey(item,x,y)
            onekey.font = self.font
            self.keys.append(onekey)
            x += 70
        y += 70
        x = 10
        row = ['a','s','d','f','g','h','j','k','l']
        for item in row:
            onekey = VirtualKey(item,x,y)
            onekey.font = self.font
            self.keys.append(onekey)
            x += 70
            
        onekey = VirtualKey('ENTER',x,y,138)
        onekey.font = self.font
        onekey.enter = True
        self.keys.append(onekey)
        
        x = 10
        y += 70        
        onekey = VirtualKey('SPACE',x,y,138)
        onekey.font = self.font
        self.keys.append(onekey)
        x += 140
        
        row = ['z','x','c','v','b','n','m']
        for item in row:
            onekey = VirtualKey(item,x,y)
            onekey.font = self.font
            self.keys.append(onekey)
            x += 70
        onekey = VirtualKey('SHIFT',x,y,138)
        onekey.font = self.font
        self.keys.append(onekey)
            
        
    def paintkeys(self):
        ''' Draw the keyboard (but only if they're dirty.) '''
        for key in self.keys:
            key.draw(self.screen, self.background, self.caps)
        
        pygame.display.flip()
    
    def clear(self):    
        ''' Put the screen back to before we started '''
        self.screen.blit(self.background,(0,0))
        pygame.display.flip()
        
        
