#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

from ErrorsHandler import *

from string import strip, find, split, lower, rjust, atoi, atof, replace, digits, zfill, join
from tools import cleanlist, which, filecopy, mkdirtree, touch, listmatch, rm, escapedfilename
from tools import get_username, get_tempdir, cmdexec
import os, os.path
import mp3info, ogg.vorbis

logfile = 'decoder.log'
logger.InitAll(logfile, '') 
sys.stdout.save = False

class Decoder:
    def __init__(self):
        """ Converts mp3/ogg-files to wav-files. """
        #logger.debug2("Decoder class instantiated")
        pass

    def convert2wav(self, files, targetPath):
        """walk files list and apply decode() to each"""

        i = 0
        for source in files:
            target = targetPath + "/" + str(i) + ".wav"
            #logger.info("Decoding %s to %s ..." % (source, target))
            logger.info("Decoding %s ..." % os.path.basename(source))
            self.decode(source, target)
            i += 1

        logger.info("Decoding finished")

    def decode(self, filename, target):
        """decode a file to wav"""
        if not os.path.isfile(filename):
            logger.error("Decoding failed: %s not found" % filename)
            return False

        mp3count = 0
        oggcount = 0
        if (lower(filename[-4:]) == ".mp3"):
            mp3count = mp3count + 1
        if (lower(filename[-4:]) == ".ogg"):
            oggcount = oggcount + 1

        # Check whether mpg123 and oggdec exists
        mpg123_command = which("mpg123")
        oggdec_command = which("oggdec")
        if ((mp3count > 0) and (mpg123_command == "")):
            logger.warn( "mpg123 not found for converting mp3 files" )
        if ((oggcount > 0) and (oggdec_command == "")):
            logger.warn( "oggdec not found for converting ogg files" )

        #logger.info( "Converting %d file(s) now" % (mp3count + oggcount) )

        if ((mp3count > 0) or (oggcount > 0)):
            #if (lower(filename[-4:]) == ".mp3") or (lower(filename[-4:]) == ".ogg"):
                #wavfilename = "%s/%s.wav" % (targetPath, os.path.basename(filename)[:-4])
            #logger.info( "target = " + target )

            if (lower(filename[-4:]) == ".mp3"):
                # Make sure that conversion is done with the correct sample rate
                file = open(filename, "rb")
                mpeg3info = mp3info.MP3Info(file)
                file.close()
                samplerate = mpeg3info.mpeg.samplerate
                command = "(%s --stereo -s \"%s\" | sox -t raw -r %d  -w -s -c 2 - -r 44100 -t wav \"%s\") 2>&1" % (mpg123_command, escapedfilename(filename), samplerate, escapedfilename(target))
            elif (lower(filename[-4:]) == ".ogg"):
		# get OGG samplerate
		vf = ogg.vorbis.VorbisFile(filename)
		vi = vf.info()
		samplerate = vi.rate
		channels = vi.channels

		#logger.info( 'OGG info: samplerate = %s , channels = %s' % (samplerate, channels) )
                if ( samplerate != 44100) or (channels != 2):
		    #logger.warn( 'samplerate not 44100, using sox to resample' )
                    command = "(sox \"%s\" -r 44100 -c 2 -t wav \"%s\") 2>&1" % (escapedfilename(filename), escapedfilename(target))
                else:
                    command = "%s -Q -o \"%s\" \"%s\" 2>&1" % (oggdec_command, escapedfilename(target), escapedfilename(filename))
            #logger.info( "Executing: %s" % command )
            (result, (stdout_output, stderr_output)) = cmdexec(command)

            if (result != 0):
                if (lower(filename[-4:]) == ".mp3"):
                    result = listmatch(output, "Playing")
                    output = output[result[0]:]
                return False
            else: return True


