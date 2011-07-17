#!/usr/bin/python
# -*- coding: utf-8 -*-
import ConfigParser, string

#------------------------------------------------------------------------
# load configuration values from /etc/burnstation/burnstation2.conf
#------------------------------------------------------------------------
class LoadConfig:
    def __init__(self):
        self.LoadConfig("/etc/burnstation/burnstation2.conf")
	
    def ParseConfig(self, file, config={}):
        """
        returns a dictionary with keys of the form
        <section>.<option> and the corresponding values
        """
        config = config.copy()
        cp = ConfigParser.ConfigParser()
        cp.read(file)
        for sec in cp.sections():
              name = string.lower(sec)
              for opt in cp.options(sec):
                     config[name + "." + string.lower(opt)] = string.strip(cp.get(sec, opt))
        return config
        
    def LoadConfig(self, configfile):
        """ GLOBAL CONFIGURATION VARIABLES """

        self.JoyName = 'none'

	# load the config
	self.config = self.ParseConfig(configfile)
     
        # Database name
        self.DB = self.config['database.db']

	# Database hostname or IP address
        self.DBhost = self.config['database.dbhost']

	# Database username
        self.DBuser = self.config['database.dbuser']
	
	# Database user password
        self.DBpass = self.config['database.dbpass']

	# Mountpoint for shared media directory path
        self.musicPath = self.config['paths.musicpath']

	# Spool directory path
        self.spoolPath = self.config['paths.spoolpath']
	
	# burnstation code home
        self.bshome = self.read('paths.home', '/usr/share/burnstation-client-2.0')

	# burnstation log dir
        self.logPath = self.read('paths.log', '/var/log/burnstation')

	# Server name which serves the "Info Panels"
        self.webUrl = self.config['paths.weburl']

	# Web server document root
        self.webRoot = self.read('paths.webroot', '/usr/share/burnstation-server/webspace')

	# CD-R drive (check this command: cdrecord -scanbus)
	self.burnDevice = self.config['burning.burndevice']

	# CD-R drive burn speed
	self.burnSpeed = self.config['burning.burnspeed']

	# Results listing limit
        self.treeLimit = int(self.config['debugging.treelimit'])

	# Default navigation tree type
        self.treeType = self.config['extra.treetype']
        
	# joystick type to use
        self.joyType = self.config['extra.joytype']
        
	# audio player to be used
        self.player = self.config['extra.player']
        
	# playlist length maximum limit
	self.MaxPlLength = self.config['burning.maxpllength']
	
	# playlist size maximum limit
	self.MaxPlSize = self.config['burning.maxplsize']

        # GUI size
        self.guiSizeX = int(self.read('gui.guisizex', 1018))
        self.guiSizeY = int(self.read('gui.guisizey', 742))

        # GUI position
        self.guiPosX = int(self.read('gui.guiposx', 0))
        self.guiPosY = int(self.read('gui.guiposy', 0))
        self.imgpos  = self.read('gui.imgpos', (700,110))

        # Font
        self.fontSize       = int(self.read('gui.fontsize', 11))
        self.fontSelectedFG = self.read('gui.fontselected', (200, 200, 200))
        self.fontSelectedBG = self.read('gui.fontselectedbg', (50, 30, 10))

        # joystick cursors
        self.joyCursors = int(self.read('joystick.cursors', 0))

	# info track settings
        home = self.config['infotrack.data']
        self.srcdir = home + "/isosrc"
        self.tmpdir = self.spoolPath + "temp"
        self.tmpiso = self.spoolPath + "infotrack.iso"
        self.tmphtml = self.tmpdir + "/index.htm"
        self.usersession = 'http://burnstation.kunstlabor.at/usersession.php?id='

        # cdrecord options
	if self.config['cdrecord.dummy'] == 'on':
            self.cdrecord_dummy = ' -dummy'
        elif self.config['cdrecord.dummy'] == 'off':    
	    self.cdrecord_dummy = ''
        
	#------------------------------------------------------
	# FIXME Temporal hack for Music-Reports switch (language selection issue)
        self.SWMTF = self.config['debugging.swmtf']

	#------------------------------------------------------
	# Joystick actions
        self.joymap = {}

	if self.joyType == 'saitek': # for Saitek P2600 Rumble Force Pad
            self.joymap['JoyUp']     = 4
            self.joymap['JoyDown']   = 6
            self.joymap['JoyRight']  = 0
            self.joymap['JoyLeft']   = 8
            self.joymap['JoySeek']   = 2
            self.joymap['JoyAdd']    = 1
            self.joymap['JoySwitch'] = 7
            self.joymap['JoyScroll'] = 3
            self.joymap['JoyBurn']   = 3
            self.joymap['JoyShift']  = 5
            #self.joymap['JoyReset']  = self.JoyShift + 4
            self.joymap['JoyRandom'] = 5

            doCancelStr = "press black button"
            doOkStr = 'press silver button'
            doCloseStr = doCancelStr
            doBurnStr = doOkStr
            doSwitchStr = 'button [5] changes option'
	if self.joyType == 'asia': # for GreenAsia joy
            self.joymap['JoyUp']     = 6
            self.joymap['JoyDown']   = 4
            self.joymap['JoyRight']  = 2
            self.joymap['JoyLeft']   = 3
            self.joymap['JoySeek']   = 1
            self.joymap['JoyAdd']    = 0
            self.joymap['JoySwitch'] = 7
            self.joymap['JoyScroll'] = 5
            self.joymap['JoyShift']  = 8
            self.joymap['JoyBurn']   = 8 + 9
            #self.joymap['JoyReset']  = self.JoyShift + 1
            self.joymap['JoyRandom'] = -1

            doCancelStr = "press [square] button"
            doOkStr = 'press [X] button'
            doCloseStr = doCancelStr
            doBurnStr = doOkStr
            doSwitchStr = '[R1] changes option'
	elif self.joyType == 'rumblepad': # for Logitech Wingman Rumblepad
            self.joymap['JoyUp']     = -1
            self.joymap['JoyDown']   = -1
            self.joymap['JoyRight']  = -1
            self.joymap['JoyLeft']   = -1
            self.joymap['JoySeek']   = 0
            self.joymap['JoyAdd']    = 1
            self.joymap['JoySwitch'] = 2
            self.joymap['JoyScroll'] = 3
            self.joymap['JoyShift']  = -1
            self.joymap['JoyBurn']   = 4
            self.joymap['JoyReset']  = -1
            self.joymap['JoyRandom'] = -1

            doCancelStr = "press [A] button"
            doOkStr = 'press [C] button'
            doCloseStr = doCancelStr
            doBurnStr = doOkStr
            doSwitchStr = 'S + C changes option'
        elif self.joyType == 'graz': # for joypad at burnstation Graz (papa)
            self.joymap['JoyUp']     = 7
            self.joymap['JoyDown']   = 8
            self.joymap['JoyRight']  = 9
            self.joymap['JoyLeft']   = 5
            self.joymap['JoySeek']   = 0
            self.joymap['JoyAdd']    = 3
            self.joymap['JoySwitch'] = 1
            self.joymap['JoyScroll'] = 2
            self.joymap['JoyShift']  = -1
            self.joymap['JoyBurn']   = 6
            self.joymap['JoyReset']  = -1
            self.joymap['JoyRandom'] = -1

            doCancelStr = "move Joystick LEFT <-"
            doOkStr = 'move Joystick RIGHT ->'
            doCloseStr = doCancelStr
            doBurnStr = doOkStr
            doSwitchStr = '"Switch Panels" changes option'
        else:
            doCancelStr = ""
            doOkStr = ""
            doCloseStr = doCancelStr
            doBurnStr = doOkStr
            doSwitchStr = ""

        self.doCancel = "CANCEL: %s" % doCancelStr
        self.doClose = "Close\n%s" % doCloseStr
        self.doBurn = "BURN: %s" % doBurnStr
        self.doOk = "OK: %s" % doOkStr
        self.doSwitch = 'SWITCH: %s' % doSwitchStr

    def read(self, setting, default='NoDefaultSetting'):
        if self.config.has_key(setting): return self.config[setting]
	else: return default

    def InitJoystick(self):
        pygame.display.init()
        pyjoy = pygame.joystick
        pyjoy.init() #initialize joystick module
        pyjoy.get_init() #verify initialization (boolean)


        # initialize
        num_joysticks = pyjoy.get_count()
        if num_joysticks > 0:
            stick = pyjoy.Joystick(0)
            stick.init() # now we will receive events for the joystick

            self.JoyName = stick.get_name()
	    self.GetJoyInfo()
            self.GetJoyMap()

            return stick
        else:
            return None

