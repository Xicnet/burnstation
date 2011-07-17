################
#CLIMusicPlayer v0.7#
#Author: Xavieran#
#Date:25/8/07#
#Needs pygame module to run#
#Released under the GPL v2.0#
#Acknowledgements:Marian Aldenhovel#
############################
# Downloaded from: http://www.cli-apps.org/content/show.php/CLI+Music+Player?content=68462
###########################

######
#TODO#
#Implement pause#
#######################

import pygame,time,sys,os
sys.path.append("..")
import Common
import  LoadConfig
config = LoadConfig.LoadConfig()
basedir = config.bshome
sys.path.append(config.bshome)
Common.Init(config.bshome)
import Database

Lp=1
while Lp==1:
	#MusicDir=raw_input('Please type a path to a music folder:')
	#os.chdir(MusicDir)
	Playlist=Database.GetPlaylist(11)
	print 'Playlist: '
	for file in Playlist:
		print file
	raw_input('Hit ENTER to continue.')
	try:
		for files in Playlist:
                        file = files['location']
			pygame.init()
			pygame.mixer.music.set_volume(1.0)
			pygame.mixer.music.load(file)
			print 'Now Playing %s'%file
			pygame.mixer.music.play()
			while pygame.mixer.music.get_busy():
				print "Playing %s"%file, pygame.mixer.music.get_pos()
				time.sleep(1)
	except KeyboardInterrupt:
		pygame.mixer.music.pause()
		skip=raw_input('Hit ENTER when ready to skip to the next song: ')
		if skip=='exit':sys.exit()
	except pygame.error:
		ErrorMsg=raw_input('That music file does not exist.\nPlease try again.\n\
Type "exit" to exit:')
		if ErrorMsg=='exit':
			print 'Exiting...',sys.exit()
