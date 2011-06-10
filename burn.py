#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
burn.py - burn script for the burnstation
"""

import sys, os
import os.path
import string
import shutil

from tools import cmdexec

import  LoadConfig
config = LoadConfig.LoadConfig()
sys.path.append(config.bshome)
from ErrorsHandler import *

# set current working directory to burnstation's home
os.chdir(config.bshome)

from decoder import Decoder

#logfile = 'burner.log'
#logger.InitAll(logfile, '')
#sys.stdout.save = True

#----------------------------------------------------------------------
def burnCD(tracks, mode):

    #-----------------------------------------------------------
    cdrecord_cmd_args = 'dev=%s' % config.burnDevice
    #cdrecord_cmd_args += ' speed=40'
    #cdrecord_cmd_args += ' speed=%d' % config.burnSpeed
    cdrecord_cmd_args += ' gracetime=2'
    cdrecord_cmd_args += ' -tao'
    cdrecord_cmd_args += ' -v'
    cdrecord_cmd_args += ' -driveropts=burnfree'
    #cdrecord_cmd_args += ' -fs=32m'
    #cdrecord_cmd_args += ' -s'
    cdrecord_cmd_args += config.cdrecord_dummy
    cdrecord_cmd_args += config.cdrecord_eject
    #-----------------------------------------------------------

    if mode == 'AUDIO':
        #self.produceHtmlInfo(tracksListResult)

        count = len(tracks)

        tracks_list = ''
        for n in range(0,count):
            tracks_list += config.spoolPath + '%i.wav ' % n

        # disabled code from pi, textinfo was not lately tested
        #cdrecord_cmd = "cdrecord %s -defpregap=0 -audio -pad -useinfo -text %s" % (cdrecord_cmd_args, listaWav)

        cdrecord_cmd = "(cdrecord %s -defpregap=0 -audio -pad %s) " % (cdrecord_cmd_args, tracks_list)

        #logger.info("Executing cdrecord with the following options: %s" % cdrecord_cmd)

        #(result, (stdout_output, stderr_output)) = cmdexec(cdrecord_cmd)
        CdrecordStatus = os.system(cdrecord_cmd + " > " + config.logPath + "/burn.log 2> " + config.logPath + "/burn.err")

        #logger.debug("CdrecordStatus before burning InfoTrack was: %s" % CdrecordStatus)

    elif mode == 'DATA':
        # join tracks array for command line
        tracks_list = '"' + string.join(tracks, '" "') + '"'

        # define where to dump the created .iso to be burnt
	ISOfile = config.spoolPath + '/burnstation.iso'
        
	# produce html
	#produceHtmlInfo(tracksListResult)
        
	# add HTML page plus contents to ISO list
        #lista += ' ' + config.tmpdir + '/*'
	
        logger.debug("*** ISOfile: %s" % ISOfile)
        
        # prepare mkisofs command to create image
        mkiso_cmd = 'mkisofs -R -o'
        mkiso_cmd += ' ' + ISOfile
        mkiso_cmd += ' -graft-points ' + tracks_list
        
        logger.debug("* Running mkisofs: %s" % mkiso_cmd)
        
        # now run it
        mkisoResult = os.system(mkiso_cmd + " > " + config.logPath + "/burn.log 2> " + config.logPath + "/burn.err")
        logger.debug('* mkisoResult: %s' % mkisoResult)

        #cdrecord_cmd = "cdrecord -dummy dev=0,0,0 gracetime=2 -s -eject -data speed=8 %s" % ISOfile
        cdrecord_cmd = "cdrecord %s -data %s" % (cdrecord_cmd_args, ISOfile)
        logger.debug("* Running cdrecord: %s" % cdrecord_cmd)
        CdrecordStatus = os.system(cdrecord_cmd + " > " + config.logPath + "/burn.log 2> " + config.logPath + "/burn.err")

    elif mode == 'USB':
        logger.info("Copying to USB")
        # join tracks array for command line
        tracks_list = '"' + string.join(tracks, '" "') + '"'

        logger.debug("* Tracks list: %s" % tracks_list)
        
        target_path = "/media/usburn/burnstation"
        if not os.path.isdir(target_path):
            os.mkdir(target_path)

        for track in tracks:
            filename = os.path.basename(track)
            try:
                shutil.copyfile(track, "%s/%s" % (target_path, filename))
            except Exception, e:
                logger.error("while trying to copy file: %s to %s . EXCEPTION: %s" % (track, target_path, str(e)))
        usb_result = os.system("echo USB_DONE > " + config.logPath + "/burn.log")
        logger.debug('* usb_result: %s' % usb_result)





        #if False and CdrecordStatus is 0:
        if False:
            #----------------------------------------------------------------------------
            ## start code by pi@modular-t.org ##

            ## make isofilesystem ##
            count = count + 1
            #mkiso = 'mkisofs -V "Burnstation" -JR -hfs -hide-hfs AUTORUN.INF -auto index.htm -map /usr/local/burnstation/isosrc/mkisofs.map -o %s -C `/usr/bin/cdrecord dev=0,0 -msinfo` %s' % (config.tmpiso, config.tmpdir)
            mkiso = 'mkhybrid -J -R -o %s -V "BurnS%s" -C `/usr/bin/cdrecord dev=0,0 -msinfo` %s' % (config.tmpiso, self.playlistID, config.tmpdir)
            logmsg = "making iso using command: %s" % mkiso
            logger.debug(logmsg)
            os.system(mkiso)
        
            # burn the datatrack
            count = count + 1
            keepGoing = ProgDlg.Update(count, 'Wait..now burning content information')
            cdrecord_cmd = "cdrecord %s -data -pad %s" % (cdrecord_cmd_args, config.tmpiso)
            logmsg = "writing iso track: %s" % cdrecord_cmd
            logger.debug(logmsg)
            CdrecordStatus = os.system(cdrecord_cmd)

            # fixate the CD
            count = count + 1
            keepGoing = ProgDlg.Update(count, 'Wait..now finishing CD. DO NOT REMOVE it until I tell you!')
            cdrecord_cmd = "cdrecord %s -fix" % cdrecord_cmd_args
            CdrecordStatus = os.system(cdrecord_cmd)
            ## end code by pi@modular-t.org ##
        
    elif mode is 'data':
        keepGoing = ProgDlg.Update(count, "Creating ISO for DATA-CD burn..wait")
        # define where to dump the created .iso to be burnt
        ISOfile = config.spoolPath + '/burnstation.iso'
        
        # produce html
        self.produceHtmlInfo(tracksListResult)
        
        # add HTML page plus contents to ISO list
        lista += ' ' + config.tmpdir + '/*'
        
        logger.debug("*** ISOfile: %s" % ISOfile)
        
        # prepare mkisofs command to create image
        mkiso_cmd = 'mkisofs -R -o'
        mkiso_cmd += ' ' + ISOfile
        mkiso_cmd += ' -graft-points ' + lista
        
        logger.debug("*** running mkiso_cmd = %s" % mkiso_cmd)
        
        # now run it
        mkisoResult = os.system(mkiso_cmd)
        logger.debug('-------------> mkisoResult: %s' % mkisoResult)

        count = count + 1

#---------------------------------------------
def produceHtmlInfo(tracksListResult):
    # prepare tempfiles
    if not os.path.isdir(config.tmpdir):
        # create the temp dir as it does not exist
        os.mkdir(config.tmpdir)

    os.system("cp " + config.srcdir + "/*png " + config.tmpdir)
    os.system("cp " + config.srcdir + "/*ico " + config.tmpdir)
    os.system("cp " + config.srcdir + "/autorun* " + config.tmpdir)
    os.system("cp " + config.bshome + "/ogghelp/* " + config.tmpdir)

    listtext = ''

    tracksList = Database.GetPlaylist(tracks)
    for record in tracksListResult:
        #sql = "SELECT tr.name, ar.name, al.name, la.name, tr.id FROM netjuke_tracks tr, netjuke_artists ar, netjuke_albums al, netjuke_labels la WHERE tr.ar_id=ar.id AND tr.al_id=al.id AND tr.la_id=la.id AND tr.id='%s'" % record
            
            listtext = listtext+"<tr style='background-color:#d3d2d2'>\n"
            listtext = listtext+"<td><a href='http://db.burnstation.org/infopanel.php?id=%s&type=song'>" % Xrecord[4] #track_id
            listtext = listtext+"%s</a></td>" % record[0] #track
            listtext = listtext+"<td>%s</td>" % record[2] #album
            listtext = listtext+"<td>%s</td>" % record[1] #artist
            listtext = listtext+"<td>%s</td>\n" % record[3] #label
            listtext = listtext+"</tr>\n" 

    # close database connection, REMEMBER to OPEN again if you need to query ;-)
    db.close()
	
    # generate HTML page to dump on datatrack with compilation info
    indexpart0 = open(config.srcdir+"/index.part0", "r")
    htmltext = indexpart0.read()
    indexpart0.close

    htmltext = htmltext+listtext

    timenow = timestamp = datetime.datetime.now().strftime("%d/%m/%Y")
    htmltext = htmltext + '<tr><td style="background-color: white" colspan="4" align="center">\n'
    htmltext = htmltext + '<br>Created with <a href="http://www.burnstation.org">'
    htmltext = htmltext + "http://www.burnstation.org</a> on %s\n" % timenow
    htmltext = htmltext + '<br> User/Session ID: <a href="%s%s">%s</a>\n' % (config.usersession, self.playlistID, self.playlistID)
    htmltext = htmltext + '<br> <a href="http://www.platoniq.net"> http://www.platoniq.net</a>\n'
    htmltext = htmltext + "</td></tr>\n"
    htmltext = htmltext + "\n"
    htmltext = htmltext + "</td></tr></table>\n"
        
    indexpart1 = open(config.srcdir+"/index.part1", "r")
    htmltext = htmltext + indexpart1.read()
    indexpart1.close
        
    ## save html to a file ##
    writeme = open(config.tmphtml, "w")
    writeme.write(htmltext)
    writeme.close()



#----------------------------------------------------------------------
def get_tracks(args):
    """Extract the list of files to burnt from the command line arguments"""

    # remove 1st element which is this script's name
    args.pop(0)
    # remove 2nd element which is the burning mode
    args.pop(0)

    return args
        
#----------------------------------------------------------------------
if __name__ == '__main__':
    logger.info("burn script executing")
    mode = sys.argv[1]
    tracks = get_tracks(sys.argv)

    #logger.info("About to burn in '%s' mode. Using temporary (spool) dir: %s " % (mode, config.spoolPath))
    #logger.info("Tracks list to be burnt: " + str(tracks))

    if mode == 'AUDIO':
        decoder = Decoder()
        decoder.convert2wav(tracks, config.spoolPath)

    burnCD(tracks, mode)

