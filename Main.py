#!/usr/bin/env python
"""
burnstation - free media distribution system
"""

DIRECTION_UP = 0
DIRECTION_DOWN = 1
DIRECTION_LEFT = 2
DIRECTION_RIGHT = 3

#Import Modules
import sys, os, pygame
from pygame.locals import *

import Common
from LoadConfig import config

basedir = config.bshome
sys.path.append(config.bshome)
Common.Init(config.bshome)

import DBcheck
if not DBcheck.exists():
    print "ERROR: Database does not exist, impossible to create it. Ask for help!"
    sys.exit(1)

# set current working directory to burnstation's home
os.chdir(basedir)

from form import Form

from scroller import Scroller

from text import *

from player import Player as MusicPlayer
from burner import Burner
from MiscTools import *

from playlist import Playlist
from MusicBrowser import MusicBrowser

from button import Button

"""Start burnstation daemon"""
d = "/usr/share/burnstation-client-2.0/daemon"
sys.path.append(d)
cmd = d+'/burnstation_daemon.py'
args = [cmd, 'start']
bs_daemon_PID = os.spawnvpe(os.P_WAIT, cmd, args, os.environ)
cmd = d+'/usb_daemon.py'
args = [cmd, 'start']
usb_daemon_PID = os.spawnvpe(os.P_WAIT, cmd, args, os.environ)

# write this process' pid somewhere to kill it easily
f = config.logPath+"/PID"
fd = open(f, "w")
fd.write( str( os.getpid() ) )
fd.close()

#sys.exit(0)

"""
sys.path.append("tools")
import inputbox
import virtkeyboard
mykeys = virtkeyboard.VirtualKeyboard()
"""

if not pygame.font: logger.info('Warning, fonts disabled')
if not pygame.mixer: logger.info('Warning, sound disabled')

APP_NAME="burn station 2.0-beta"

from globals import *
from ActionManager import *

#---------------------------------------------------------------------------------
class EventManager:
        """this object is responsible for coordinating most communication
        between the Model, View, and Controller."""
        def __init__(self ):
            """
            from weakref import WeakKeyDictionary
            self.listeners = WeakKeyDictionary()
            """

            self.current = None

            self.listeners = {}
            self.eventQueue= []

        #----------------------------------------------------------------------
        def RegisterListener( self, name, listener ):
            if name not in self.listeners:
                self.listeners[name] = listener
                self.listeners[name].isFocused = False

        #----------------------------------------------------------------------
        def UnregisterListener( self, listener ):
            if listener in self.listeners.keys():
                del self.listeners[ listener ]

        #----------------------------------------------------------------------
        def SetFocus( self, listener ):
            sprite = self.listeners[listener].sprite

            self.prefocus = self.current
            self.current = listener
            sprite.SetFocus(1)
            sprite.isFocused = True

            logger.debug("Set focus to: %s" % listener)

        #----------------------------------------------------------------------
        def SetUnFocus( self, listener ):
            sprite = self.listeners[listener].sprite

            sprite.SetFocus(0)
            sprite.isFocused = False
            logger.debug( "UNFOCUSED: %s" % listener )

        #----------------------------------------------------------------------
        def GetFocused( self ):
            return self.current

        #----------------------------------------------------------------------
        def Post( self, event ):
            if not isinstance(event, TickEvent):
                pass #logger.debug( "     Message: " + str(event.name) )

            for listener in self.listeners.keys():
                #NOTE: If the weakref has died, it will be 
                #automatically removed, so we don't have 
                #to worry about it.
                self.listeners[listener].Notify( event )


#---------------------------------------------------------------------------------
class CPUSpinnerController:
    def __init__(self, evManager):
            self.evManager = evManager
            self.evManager.RegisterListener( 'cpu', self )

            self.keepGoing = 1

    #----------------------------------------------------------------------
    def Run(self):
        while self.keepGoing:
            event = TickEvent()
            self.evManager.Post( event )

    #----------------------------------------------------------------------
    def Notify(self, event):
        if isinstance( event, QuitEvent ):
            self.keepGoing = 0

#---------------------------------------------------------------------------------
class PygameView:
    def __init__(self, evManager):
        self.evManager = evManager
        self.evManager.RegisterListener( 'view', self )

        #Initialize Everything
        pygame.mixer.pre_init(44100,-16,2, 1024 * 2)
        pygame.init()
        self.screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
        if config.fullscreen: pygame.display.toggle_fullscreen()
        pygame.display.set_caption(APP_NAME)
        self.background = pygame.Surface( self.screen.get_size() )
        self.background.fill( (0,0,0) )

        pygame.mouse.set_visible(1)

        self.backSprites = pygame.sprite.RenderUpdates()
        self.frontSprites = pygame.sprite.RenderUpdates()
        self.MusicBrowserSprites = pygame.sprite.RenderUpdates()
        self.topSprites = pygame.sprite.RenderUpdates()

        self.browser_type = 'labels'
        #self.browser_type = 'path'
        #self.browser_type = 'jamendo'

        t = TextSprite(self.frontSprites, APP_NAME, 32, 300, 30, RED)
        title = t.Show()
        t.rect = (0,0)

        #userinput = mykeys.run(self.screen, "type something")
        #answer = inputbox.ask(self.screen, "Your name")

    #----------------------------------------------------------------------
    def ShowPublish(self, charactor):
        """label selection charactor-sprite"""

        charactor.sprite = Form(self.topSprites)
        charactor.sprite.SetTitle("Which label?")
        charactor.sprite.SetFields(["  Label Name"])
        charactor.sprite.rect = (400,900)

    #----------------------------------------------------------------------
    def ShowRegister(self, charactor):
        """register charactor-sprite"""

        charactor.sprite = Form(self.topSprites)
        charactor.sprite.SetTitle("Register")
        charactor.sprite.SetFields(["        Name", "       E-mail", "Password"])
        charactor.sprite.rect = (400,900)

    #----------------------------------------------------------------------
    def ShowLogin(self, charactor):
        """login charactor-sprite"""

        charactor.sprite = Form(self.topSprites)
        charactor.sprite.SetTitle("Login")
        charactor.sprite.SetFields(["       E-mail", "Password"])
        charactor.sprite.user = None
        charactor.sprite.rect = (400,900)

    #----------------------------------------------------------------------
    def ShowBurner(self, charactor):
        # burner charactor-sprite
        charactor.sprite = Burner(self.topSprites, self.screen, 400, 400)
        sector = charactor.sector
        sectorSprite = self.GetSectorSprite( sector )
        charactor.sprite.rect = (400,900)

    #----------------------------------------------------------------------
    def ShowPlaylist(self, charactor):
        # build burnlist
        charactor.sprite = Playlist(self.frontSprites, self.browser_type)
        charactor.sprite.rect = (500,30)
        charactor.sprite.browser.rect = (500,30)

    #----------------------------------------------------------------------
    def ShowMusicPlayer(self, charactor):
        # player controls
        charactor.sprite = MusicPlayer(self.frontSprites, self.screen, 0, 25)
        charactor.sprite.rect = (10,25)

    #----------------------------------------------------------------------
    def ShowMusicBrowser(self, charactor):
        # content browser
        charactor.sprite    = MusicBrowser(self.MusicBrowserSprites, self.browser_type)
        self.evManager.SetFocus('musicbrowser')

    #----------------------------------------------------------------------
    def GetSectorSprite(self, sector):
        for s in self.backSprites.sprites():
            if hasattr(s, "sector") and s.sector == sector:
                return s

    #----------------------------------------------------------------------
    def Notify(self, event):
        #print "view"
        if isinstance( event, TickEvent ):
            sprites = self.evManager.listeners
            sprites['musicbrowser'].sprite.loop()
            sprites['musicplayer'].sprite.loop()
            sprites['burner'].sprite.loop()
            #sprites['login'].sprite.loop()

            #Draw Everything
            self.backSprites.clear( self.screen, self.background )
            self.frontSprites.clear( self.screen, self.background )
            self.MusicBrowserSprites.clear( self.screen, self.background )
            self.topSprites.clear( self.screen, self.background )

            self.backSprites.update()
            self.frontSprites.update()
            self.topSprites.update()
            self.MusicBrowserSprites.update()

            dirtyRects1 = self.backSprites.draw( self.screen )
            dirtyRects2 = self.frontSprites.draw( self.screen )
            dirtyRects3 = self.topSprites.draw( self.screen )
            dirtyRects4 = self.MusicBrowserSprites.draw( self.screen )

            dirtyRects = dirtyRects1 + dirtyRects2 + dirtyRects3 + dirtyRects4
            pygame.display.update( dirtyRects )

        elif isinstance( event, CharactorPlaceEvent ):

            if   event.charactor.name == 'musicplayer' : self.ShowMusicPlayer( event.charactor )
            elif event.charactor.name == 'musicbrowser': self.ShowMusicBrowser( event.charactor )
            elif event.charactor.name == 'playlist'    : self.ShowPlaylist( event.charactor )
            elif event.charactor.name == 'burner'      : self.ShowBurner( event.charactor )
            elif event.charactor.name == 'login'       : self.ShowLogin( event.charactor )
            elif event.charactor.name == 'register'    : self.ShowRegister( event.charactor )
            elif event.charactor.name == 'publish'    : self.ShowPublish( event.charactor )
            
        elif isinstance( event, CharactorMoveEvent ):
            self.MoveCharactor( event.charactor )

    #----------------------------------------------------------------------
    def MoveCharactor(self, charactor):
        sprites = self.evManager.listeners
        action = charactor.action
        current = self.evManager.GetFocused()

        if charactor.name == 'musicplayer':
            logger.debug("************************ in MoveCharactor() action: %s" % str(action) )
            if action == 'PLAY':
                sprites['musicplayer'].sprite.Play("file://" + sprites[current].sprite.browser.list[sprites[current].sprite.selected]['location'])
                sprites['musicplayer'].sprite.SetPlaytime(sprites[current].sprite.browser.list[sprites[current].sprite.selected]['seconds'])
                sprites['musicplayer'].sprite.SetNowPlaying(sprites[current].sprite.browser.list[sprites[current].sprite.selected]['name'])

        ########################
        ### global keys
        if charactor.name == 'burner':
            sprite = sprites['burner'].sprite

        """
            if sprite.visible:
                if action == 49: # 1 = burn audio
                    logger.debug("*** BURN AUDIO")
                    tracks = ""
                    list = sprites['playlist'].sprite.browser.list
                    for i in range(len(list)):
                        tracks += list[i]['location']+":"
                    sprite.BurnCD(tracks)


        if charactor.name == 'musicplayer':
            if action == 120: # x = stop
                sprites['musicplayer'].sprite.Stop()
            elif action == 99:  # c = seek
                sprites['musicplayer'].sprite.Seek('fwd')
            #elif action == 57: # 9 = volume down
            #    sprites['musicplayer'].sprite.VolumeDown()
            #elif action == 48: # 0 = volume up
            #    sprites['musicplayer'].sprite.VolumeUp()
        ########################
        """

    #----------------------------------------------------------------------
    def GetCharactorSprite(self, charactor):
        for s in self.frontSprites.sprites():
            if hasattr(s, "sector"): print s
            return s

#------------------------------------------------------------------------------
class Game:
    """..."""

    STATE_PREPARING = 0
    STATE_RUNNING = 1
    STATE_PAUSED = 2

    #----------------------------------------------------------------------
    def __init__(self, evManager):
        self.evManager = evManager
        self.evManager.RegisterListener( 'game', self )

        self.state = Game.STATE_PREPARING
        
        self.players = [ Player(evManager) ]
        self.map = Map( evManager )

    #----------------------------------------------------------------------
    def Start(self):
        self.map.Build()
        self.state = Game.STATE_RUNNING
        ev = GameStartedEvent( self )
        self.evManager.Post( ev )

    #----------------------------------------------------------------------
    def Notify(self, event):
        if isinstance( event, TickEvent ):
            if self.state == Game.STATE_PREPARING:
                self.Start()

#------------------------------------------------------------------------------
class Player:
    """..."""
    def __init__(self, evManager):
        self.evManager = evManager
        #self.evManager.RegisterListener( self )

        self.charactors = [
                            Charactor('musicbrowser', evManager),
                            Charactor('playlist', evManager),
                            Charactor('musicplayer', evManager),
                            Charactor('burner', evManager),
                            Charactor('login', evManager),
                            Charactor('register', evManager),
                            Charactor('publish', evManager)
                           ]

#------------------------------------------------------------------------------
class Charactor:
    """..."""
    def __init__(self, name, evManager):
        self.name = name
        self.evManager = evManager
        self.evManager.RegisterListener( name, self )
        self.sector = None

    #----------------------------------------------------------------------
    def Move(self, action):
        self.action = action
        ev = CharactorMoveEvent( self )
        self.evManager.Post( ev )

    #----------------------------------------------------------------------
    def Place(self, sector):
        self.sector = sector
        ev = CharactorPlaceEvent( self )
        self.evManager.Post( ev )

    #----------------------------------------------------------------------
    def Notify(self, event):

        if isinstance( event, GameStartedEvent ):
            map = event.game.map
            self.Place( map.sectors[map.startSectorIndex] )

        elif isinstance( event, CharactorMoveRequest ):
            self.Move( event.action )


#------------------------------------------------------------------------------
class Map:
    """..."""
    def __init__(self, evManager):
        self.evManager = evManager
        #self.evManager.RegisterListener( self )

        self.sectors = range(9)
        self.startSectorIndex = 0

    #----------------------------------------------------------------------
    def Build(self):
        for i in range(9):
            self.sectors[i] = Sector( self.evManager )

        ev = MapBuiltEvent( self )
        self.evManager.Post( ev )

#------------------------------------------------------------------------------
class Sector:
    """..."""
    def __init__(self, evManager):
        self.evManager = evManager
        #self.evManager.RegisterListener( self )

        self.neighbors = range(4)

        self.neighbors[DIRECTION_UP] = None
        self.neighbors[DIRECTION_DOWN] = None
        self.neighbors[DIRECTION_LEFT] = None
        self.neighbors[DIRECTION_RIGHT] = None

    #----------------------------------------------------------------------
    def MovePossible(self, action):
            return 1


#---------------------------------------------------------------------------------
def main():
    """this function is called when the program starts.
       it initializes everything it needs, then runs in
       a loop until the function returns."""

    evManager = EventManager()

    keybd = KeyboardController( evManager )
    spinner = CPUSpinnerController( evManager )
    pygameView = PygameView( evManager )
    game = Game( evManager )

    spinner.Run()

    eight = 0
    nine = 0
#Prepare Game Objects
    clock = pygame.time.Clock()


        #userinput = mykeys.run(screen, "text")
#Game Over


#this calls the 'main' function when this script is executed
if __name__ == '__main__': main()


