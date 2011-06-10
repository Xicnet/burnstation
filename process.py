#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Miscellaneous functions to manage unix processes

"""

from commands import getoutput
from string import split, atoi, ljust, strip, find, upper, join
from types import ListType, StringType, DictType

import sys
import ErrorsHandler
import re
import tools

# Boolean constants
TRUE = 1
FALSE = 0

# Define some necessary constants
FILTERON = 1
FILTEROFF = 0

FILTERMODEEXACT = 1
FILTERMODESUB = 2

# Operating system depended ps parameters
OSTYPEBSD = "BSD"
OSTYPESYSV = "System V"
OSTYPEUNKNOWN = "Unknown"
OSTYPESUNOSUCB = "SunOS UCB"

# The platform can be determined by executing 
#     python -c "import sys;print sys.platform"

osFamily = {}
osFamily[OSTYPEBSD] = ["freebsd4", "bsdos4"]
osFamily[OSTYPESYSV] = ["linux-i386", "linux2" ]
osFamily[OSTYPESUNOSUCB] = ["sunos5"]

osPsParam = {}
osPsParam[OSTYPEBSD] = "-j -p %s"
osPsParam[OSTYPESYSV] = "-f -p %s"
osPsParam[OSTYPEUNKNOWN] = "-f -p %s"
osPsParam[OSTYPESUNOSUCB] = "-l %s"

osPsProcessListParam = {}
osPsProcessListParam["sunos5"] = "-ef"
osPsProcessListParam["linux2"] = "ax"
osPsProcessListParam[OSTYPEUNKNOWN] = "ax"

# Definition of the ProcessTable class
class ProcessTable:

    # ProcessTable default settings
    processes = {}                                 # List of Dictionaries containing processes
    parameter = ""                                 # Parameters passed to read
    processmap = {}                                # Dictionary containing the various columns
    columnlength = {}                              # Dictionary containing the maximum length of each column
    filteredpids = []                              # List of filtered pids
    mode = FILTEROFF                               # Current mode
    ppidparam = ""

    def __init__(self):
        """ Initialize the process class. """

        self.__ProcessTable_ps_command = tools.which("ps")

    def read(self, parameter = None):
        """ Reads the current processes with optional parameters. """

        if (parameter == None):
            if (osPsProcessListParam.has_key(sys.platform)):
                parameter = osPsProcessListParam[sys.platform]
            else:
                parameter = osPsProcessListParam[OSTYPEUNKNOWN]
        self.processes = {}
        self.parameter = parameter
        self.reread()

    def __ProcessTable_regexp(self, columns, command):
        """ Create a regular expression for the given list of columns. """
        strRegExp = " *"
        for intCounter in range(len(columns)):
            column = upper(columns[intCounter])
            if ((column == "UID") or (column == "USER")):
                # Strings e.g. 'root'
                strRegExp = "%s([\w-]+) +" % strRegExp
            elif ((column == "PID") or (column == "PPID") or (column == "RSS") or (column == "VSZ") or (column == "C")):
                # Digits e.g. 762
                strRegExp = "%s(\d+) +" % strRegExp
            elif ((column == "TIME") or (column == "STIME") or (column == "START")):
                # Time columns: Oct 02, Oct02, 02:10, 00:01:15
                strRegExp = "%s(\w{3} {0,1}\d+|\d+:\d+:\d+|\d+:\d+) +" % strRegExp
            elif (column == "STAT"):
                # Status: S, W, N, R, L, <
                strRegExp = "%s([SWNRL<]+) +" % strRegExp
            elif (column == "TTY"):
                # TTY: ?, pty/1, console
                strRegExp = "%s(\?|[\w/]+\d*) +" % strRegExp
            elif ((column == "CMD") or (column == "COMMAND")):
                # Command: a string at the end of the line
                strRegExp = "%s(.+)$" % strRegExp
            elif ((column == "%CPU") or (column == "%MEM")):
                # Digits with a comma
                strRegExp = "%s(\d+\.\d+) +" % strRegExp
            else:
                logger.error("Unknown column '%s' in output of '%s'. Please send the output of '%s' to Martin.Preishuber@eclipt.at." % (column, command, command))
        logger.debug("Regular expression: %s" % strRegExp)
        return strRegExp

    def __ProcessTable_check_ps_output(self, cmdoutput):
        # this is a workaround for buggy ps output on some 2.6 kernels
        if (strip(cmdoutput[0])[0:17] == "Unknown HZ value!"):
            cmdoutput = cmdoutput[1:]
        return cmdoutput

    def reread(self):
        """ Re-read processes list (no parameters necessary). """

        command = "%s %s" % (self.__ProcessTable_ps_command, self.parameter)
        logger.debug("Reading process table with command: %s" % command)

        output = getoutput(command)
        splitted = split(output, "\n")
        splitted = self.__ProcessTable_check_ps_output(splitted)
        self.processmap = tools.cleanlist(split(splitted[0], " "))
        processes = splitted[1:]
        regexp = re.compile(self.__ProcessTable_regexp(self.processmap, command))

        self.processes = {}
        for i in range(len(processes)):
            process = processes[i]
            matchobject = regexp.match(process)
            if (not matchobject):
                if (strip(process) != ""):
                    logger.warn("The process line '%s' does not match the given regular expression." % process)
            else:
                processentry = {}
                for j in range(len(self.processmap)):
                    processentry[self.processmap[j]] = matchobject.group(j + 1)
                    if (self.processmap[j] == "PID"):
                        pid = atoi(matchobject.group(j + 1))
                self.processes[pid] = processentry

    def filter(self, filters = None, filtermode = FILTERMODEEXACT):
        """
        Filter for certain conditions in the ProcessTable.
        filters is a dictionary containing parameter:[valuelist]
        """

        logger.debug("Applying filter: (%s, %d)" % (str(filters), filtermode))
        self.mode = FILTERON
        self.filteredpids = []

        for i in range(len(self.processes.keys())):

            processid = self.processes.keys()[i]
            process = self.processes[processid]

            processmatches = TRUE
            for j in range(len(filters.keys())):

                filtername = filters.keys()[j]
                filterlist = filters[filtername]
                if type(filterlist) != ListType:
                    filterlist = [filterlist]
                filtername = upper(filtername)

                # special case for different ps implementations
                if (filtername == "CMD") and (process.has_key("COMMAND")):
                    filtername = "COMMAND"

                parameter = process[upper(filtername)]

                for k in range(len(filterlist)):
                    singlefilter = filterlist[k]
                    if (filtermode == FILTERMODEEXACT) or (type(singlefilter) != StringType):
                        if (str(singlefilter) <> str(parameter)):
                            processmatches = FALSE
                    else:
                        if (find(parameter, singlefilter) < 0):
                            processmatches = FALSE

            if (processmatches == TRUE):
                self.filteredpids.append(atoi(process["PID"]))
    
    def removefilter(self):
        """ Remove applied filter. """

        logger.debug("Removing filter.")
        self.filteredpids = []
        self.mode = FILTEROFF

    def exists(self, filters = None, filtermode = FILTERMODEEXACT):
        """ Checks, wether a process specified by the given condition(s) exists. """

        tempfilter = self.filteredpids
        self.filter(filters, filtermode)
        exists = (len(self.filteredpids) > 0)
        self.filteredpids = tempfilter

        return exists

    def process(self, pid):
        """ Returns a dictionary with the specified process. """

        if (self.processes.has_key(pid)):
            return self.processes[pid]
        else:
            return None

    def printtable(self, list = None):
        """ Print the process table (optional just a list of given pids). """

        if (list == None):
            list = self.processes.keys()
        elif (type(list) == DictType):
            list = list.keys()
        list.sort()

        if len(list) == 0:
            return

        sys.stdout.write("%s\n" % strip(join(self.processmap)))

        for i in range(len(list)):
            if (self.processes.has_key(list[i])):
                process = self.processes[list[i]]
                line = ""
                for j in range(len(process.keys())):
                    line = "%s%s " % (line, process[process.keys()[j]])
                sys.stdout.write("%s\n" % line)
            else:
                sys.stdout.write("No process with pid #%s in the internal process table.\n" % list[i])

    def pids(self):
        """ Returns either all pids or all filtered pids. """

        if (self.mode == FILTERON):
            list = self.filteredpids
        else:
            list = self.processes.keys()
        list.sort()
        return list

    def ppids(self, pids = None):
        """ Returns a dictionary of parent pids of given pids, filtered pids or all pids (depends on filter mode). """

        if (pids == None):
            if (self.mode == FILTERON):
                pids = self.filteredpids
            else:
                pids = self.processes.keys()
        pids.sort()
        logger.debug("Searching PPIDS of PIDS %s" % str(pids))
        ppids = {}
        for i in range(len(pids)):
            pptab = ProcessTable()

            if (self.ppidparam == ""):
                for j in range(len(osPsParam.keys())):
                    opSysFamily = osPsParam.keys()[j]
                    if (osFamily.has_key(opSysFamily)):
                        if (sys.platform in osFamily[opSysFamily]):
                            self.ppidparam = osPsParam[opSysFamily]
                if (self.ppidparam == ""):
                    logger.warn("Unknown operating system platform: %s" % sys.platform)
                    self.ppidparam = osPsParam[OSTYPEUNKNOWN]

            pptab.read(self.ppidparam % pids[i])
            ppid = pptab.process(pptab.pids()[0])["PPID"]
            if (not ppids.has_key(ppid)):
                ppids[ppid] = [pids[i]]
            else:
                ppids[ppid].append(pids[i])
        return ppids
