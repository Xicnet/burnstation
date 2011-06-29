#!/usr/bin/python
# -*- coding: utf-8 -*-
from LoadConfig import config
joyType = config.joyType
print "JOYTYPE...................: ",  joyType
joyMap = {}

#=====================================================================
# JoyPad buttons -> actions mapping
#=====================================================================

#---------------------------------------------------------------------
# DragonRise (Pinnacle E-Design)
joyMap['DragonRise'] = {}
joyMap['DragonRise']['STOP']            = 0
joyMap['DragonRise']['PLAYLIST_ADD']    = 2
joyMap['DragonRise']['SEEK_FWD']        = 1
joyMap['DragonRise']['BURN']            = 3
joyMap['DragonRise']['BROWSER_SWITCH']  = 6
joyMap['DragonRise']['GO_UP']           = 7
joyMap['DragonRise']['BROWSER_SWITCH2'] = -1
joyMap['DragonRise']['VOL_UP']          = -1
joyMap['DragonRise']['VOL_DOWN']        = -1
joyMap['DragonRise']['BURN_AUDIO']      = 0
joyMap['DragonRise']['BURN_DATA']       = 1

#---------------------------------------------------------------------
# precision
joyMap['precision'] = {}
joyMap['precision']['STOP']            = 0
joyMap['precision']['PLAYLIST_ADD']    = 1
joyMap['precision']['SEEK_FWD']        = 2
joyMap['precision']['BURN']            = 3
joyMap['precision']['BROWSER_SWITCH']  = 4
joyMap['precision']['BROWSER_SWITCH2'] = 6
joyMap['precision']['VOL_UP']          = 5
joyMap['precision']['VOL_DOWN']        = 7
joyMap['precision']['BURN_AUDIO']      = 8
joyMap['precision']['BURN_DATA']       = 9

#---------------------------------------------------------------------
# Asia
joyMap['asia'] = {}
joyMap['asia']['STOP']            = 3
joyMap['asia']['PLAYLIST_ADD']    = 2
joyMap['asia']['SEEK_FWD']        = 1
joyMap['asia']['BURN']            = 0
joyMap['asia']['BROWSER_SWITCH']  = 6
joyMap['asia']['BROWSER_SWITCH2'] = 4
joyMap['asia']['VOL_UP']          = 7
joyMap['asia']['VOL_DOWN']        = 5
joyMap['asia']['BURN_AUDIO']      = 8
joyMap['asia']['BURN_DATA']       = 9

#---------------------------------------------------------------------
# DragonCCGSM
joyMap['DragonCCGSM'] = {}
joyMap['DragonCCGSM']['STOP']            = 0
joyMap['DragonCCGSM']['PLAYLIST_ADD']    = 2
joyMap['DragonCCGSM']['SEEK_FWD']        = 1
joyMap['DragonCCGSM']['BURN']            = 4
joyMap['DragonCCGSM']['BROWSER_SWITCH']  = 6
joyMap['DragonCCGSM']['BROWSER_SWITCH2'] = 6
joyMap['DragonCCGSM']['VOL_UP']          = 99
joyMap['DragonCCGSM']['VOL_DOWN']        = 99
joyMap['DragonCCGSM']['BURN_AUDIO']      = 0
joyMap['DragonCCGSM']['BURN_DATA']       = 1


