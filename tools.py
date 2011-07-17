#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Miscellaneous functions written by Martin Preishuber

"""

from string import strip, lower, zfill, find, atoi, join, replace
from os import getcwd, chdir, mkdir, lstat, unlink, rmdir, utime, environ, getpid

import sys

from urlparse import urlparse
from time import time, sleep
from popen2 import popen3
if (sys.platform != "win32"):
    from popen2 import Popen3
from re import match

import signal
import os
import string
import copy
from ErrorsHandler import *
import process

if (sys.platform != "win32"):
    from os import wait, kill

# Boolean constants
TRUE = 1
FALSE = 0


# Color constants
BLACK = "30"
RED = "31"
GREEN = "32"
YELLOW = "33"
BLUE = "34"
PURPLE = "35"
AQUA = "36"
WHITE = "37"


"""

String operations

"""

def split(s, sep = None, special = None):
    """ Extended split (doesn't split within special characters). """
    if (special == None):
        if (sep == None):
            return string.split(s)
        else:
            return string.split(s, sep)
    else:
        list = []
        elem = ""
        mode = 0
        for i in range(len(s)):
            if (s[i] == sep):
                if (mode == 0) and (elem != ""):
                    list.append(elem)
                    elem = ""
                elif (mode == 1):
                    elem = "%s%s" % (elem, s[i])
            elif (s[i] == special):
                if (mode == 0):
                    mode = 1
                elif (mode == 1):
                    mode = 0
            else:
                elem = "%s%s" % (elem, s[i])
        list.append(elem)
        return list

def cfill(source, char, width):
    """ Fill a string with a character up to a given width. """
    while len(source) < width:
        source = "%s%s" % (source, char)
    return source

def pfill(source, char, width):
    """ Pad a string with a character up to a given width. """
    while len(source) < width:
        source = char + source
    return source

def lstrip(string):
    """ Strip blanks (NOT whitespaces) on the left side of a string. """
    while (string[0] == " ") and (len(string) > 0):
        string = string[1:]
    return string

def merge(string1, string2):
    """ Merge two strings byte-by-byte. """
    pos1 = 0
    pos2 = 0
    result = ""
    while (len(string1) >= (pos1 + 1)) and (len(string2) >= (pos2 + 1)):
        result = "%s%s%s" % (result, string1[pos1], string2[pos2])
        pos1 = pos1 + 1
        pos2 = pos2 + 1
    if (len(string1) >= (pos1 + 1)):
        result = "%s%s" % (result, string1[pos1:])
    if (len(string2) >= (pos2 + 1)):
        result = "%s%s" % (result, string2[pos2:])
    return result


"""

RE module functions

"""

def unfold(regexp):
    splitted = split(regexp, "\n")
    for i in range(len(splitted)):
        splitted[i] = strip(splitted[i])
    return join(splitted, "")


"""

Type conversion functions

"""

def bool2str(value):
    """ Converts a Boolean value to the corresponding String. """
    if (value == FALSE):
        return "False"
    elif (value == TRUE):
        return "True"
    else:
        return "Invalid boolean value: %s" % str(value)

def str2bool(value):
    """ Converts a String value to the corresponding Boolean. """
    if (lower(value) == "true") or (lower(value) == "yes") or (value == "1"):
        return TRUE
    elif (lower(value) == "false") or (lower(value) == "no") or (value == "0"):
        return FALSE
    else:
        return None

def lng2str(number, prettyprint = TRUE):
    """ Returns a string representation of a number (with a pretty-print option). """
    if (prettyprint == TRUE):
        number = list(str(number))
        if number[-1] == "L":
            number = number[:-1]
        number.reverse()
        dots = divmod(len(number) - 1, 3)[0]
        for i in range(dots):
            number.insert(3 + (i * 3) + i, ".")
        number.reverse()
        return join(number, "")
    else:
        return str(number)

"""

List operations

"""

def striplist(list):
    """ Strip each value of a list. """
    for i in range(len(list)):
        list[i] = strip(list[i])
    return list

def cleanlist(list):
    """ Removes empty entries from a list. """
    newlist = []
    for i in range(len(list)):
        if (list[i] <> ""):
            newlist.append(list[i])
    return newlist

def listdiff(list1, list2):
    """ Get the difference of two lists. """
    difflist = []
    for i in range(len(list1)):
        if (not list1[i] in list2):
            difflist.append(list1[i])
    for i in range(len(list2)):
        if (not list2[i] in list1):
            difflist.append(list2[i])
    return difflist

def listmatch(list, expression):
    """ Returns the matching element number and match object. """
    number = -1
    element = None
    for i in range(len(list)):
        if (match(expression, list[i])):
            number = i
            element = list[i]
            break
    return (number, element)

"""

Time functions

"""

def nicetime(seconds):
    """ Converts time in seconds to a nicely formatted string. """
    minutes, seconds = divmod(seconds, 60)
    return "%s:%s" % (zfill(minutes, 2), zfill(seconds, 2))


"""

File and directory operations

"""

def ls(directory, recursive = FALSE, includepath = FALSE, onlydirectories = FALSE):
    """ Creates a directory listing, optional including full filenames and recursive. """
    longlist = []
    allfiles = os.listdir(directory)
    if (directory == "."): directory = ""
    if ((len(directory) > 0) and (directory[-1] != os.sep)): directory = "%s%s" % (directory, os.sep)
    for i in range(len(allfiles)):
        filename = "%s%s" % (directory, allfiles[i])
        longfilename = "%s%s%s" % (os.path.abspath(directory), os.sep, filename)
        if (os.path.isdir(filename)):
            if (includepath == TRUE):
                longlist.append(longfilename)
            else:
                longlist.append(filename)
            if (recursive == TRUE):
                subdirlist = ls("%s%s" % (filename, os.sep), recursive, includepath, onlydirectories)
                if (len(subdirlist) > 0):
                    longlist = longlist + subdirlist
        else:
            if (onlydirectories == FALSE):
                if (includepath == TRUE):
                    longlist.append(longfilename)
                else:
                    longlist.append(filename)
    return longlist

def rm(file, maximum = -1, deleted = 0):
    """ Remove a file or directory (recursive) and return the number of directories, files, bytes & links deleted. """
    directories = files = bytes = links = 0L
    if (os.path.islink(file)):
        if (maximum == -1) or ((maximum != -1) and (deleted < maximum)):
            links = links + 1
            unlink(file)
    elif (os.path.isfile(file)):
        filesize = lstat(file)[6]
        if (maximum == -1) or ((maximum != -1) and ((deleted + filesize) < maximum)):
            bytes = bytes + filesize
            files = files + 1
            unlink(file)
    else:
        filelist = os.listdir(file)
        for i in range(len(filelist)):
            result = rm("%s%s%s" % (file, os.sep, filelist[i]), maximum, bytes)
            directories = directories + result[0]
            files = files + result[1]
            bytes = bytes + result[2]
            links = links + result[3]
        filelist = listdir(file)
        if (maximum == -1) or ((len(filelist) == 0) and (maximum != -1) and (deleted < maximum)):
            rmdir(file)
            directories = directories + 1
    return [directories, files, bytes, links]

def mkdirtree(directory):
    """ Creates a whole direcotry tree. """
    if (directory[-1:] == os.sep):
        directory = directory[:-1]
    if (not os.path.exists(directory)):
        pwd = getcwd()
        splitted = split(directory, os.sep)
        for i in range(1, len(splitted)):
            path = join(splitted[:i + 1], os.sep)
            if (not os.path.exists(path)):
                mkdir(path)
        chdir(pwd)

def du(file):
    """ Calculate the disk usage of a given directory. """
    if (os.path.islink(file)) or (os.path.isfile(file)):
        size = lstat(file)[6]
    elif (os.path.isdir(file)):
        filelist = listdir(file)
        size = 0
        for i in range(len(filelist)):
            size = size + du("%s%s%s" % (file, os.sep, filelist[i]))
    else:
        # the file is a special device (socket)
        size = 0
    return size

def __internal_which(file):
    if (file == ""):
        return ""
    for item in split(os.environ["PATH"], os.pathsep):
        filename="%s%s%s" % (item, os.sep, file)
        if (sys.platform == "win32"):
            if (os.path.exists("%s.exe" % filename)):
                return "%s.exe" % filename
            elif (os.path.exists("%s.com" % filename)):
                return "%s.com" % filename
            elif (os.path.exists("%s.bat" % filename)):
                return "%s.bat" % filename
            elif (os.path.exists("%s.cmd" % filename)):
                return "%s.cmd" % filename
        else:
            if (os.path.exists(filename)):
                return filename
    return ""
    
def which(file):
    """ Check the path to find some specified program. """
    filename = __internal_which(file)
    if (find(filename, " ") != -1):
        return "\"%s\"" % filename
    else:
        return filename

def filecopy(source, target):
    """ Copy a source file to a target file. """
    sourcefile = open(source, "r")
    targetfile = open(target, "w")
    targetfile.write(sourcefile.read())
    targetfile.close()
    sourcefile.close()

def includefile(source, target):
    """ Include a file into a already open file. """
    sourcefile = open(source, "r")
    line = "line"
    while (line != ""):
        line = sourcefile.readline()
        if (line != ""):
            target.write(line)
    sourcefile.close()

def listdir(path, incfiles = TRUE, incdirs = TRUE, inclinks = TRUE):
    """ A modified listdir with some optional parameters. """
    files = os.listdir(path)
    if ((incfiles == TRUE) and (incdirs == TRUE) and (inclinks == TRUE)):
        cleanfiles = files
    else:
        cleanfiles = []
        if (path[-1] != os.sep):
            path = "%s%s" % (path, os.sep)
        for i in range(len(files)):
            file = "%s%s" % (path, files[i])
            addFile = TRUE
            if (incfiles == FALSE) and (os.path.isfile(file)):
                addFile = FALSE
            if (incdirs == FALSE) and (os.path.isdir(file)):
                addFile = FALSE
            if (inclinks == FALSE) and (os.path.islink(file)):
                addFile = FALSE
            if (addFile == TRUE):
                cleanfiles.append(files[i])
    cleanfiles.sort()
    return cleanfiles

def touch(filename):
    """ Implements the functionality of the unix command "touch". """
    if (os.path.exists(filename)):
        now = time()
        utime(filename, (now, now))
    else:
        file = open(filename, "w")
        file.close()

def df(directory = ""):
    """ Returns the values of "df" in list form. """
    df_command = which("df")
    df_command = strip("%s --block-size=1 %s" % (df_command, directory))
    output = striplist(cmdoutput(df_command)[1:])
    entry_list = []
    for i in range(len(output)):
        splitted = cleanlist(split(output[i], " "))
        entry = {}
        entry["FILESYSTEM"] = splitted[0]
        entry["SIZE"] = atoi(splitted[1])
        entry["USED"] = atoi(splitted[2])
        entry["AVAILABLE"] = atoi(splitted[3])
        entry["PERCENTAGE"] = atoi(splitted[4][:-1])
        entry["MOUNT_POINT"] = splitted[5]
        entry_list.append(entry)
    return entry_list

def cmpdirs(dict1, dict2):
    """ Compares two dictionaries of lstatfiles and returns a tuple ( {added}, {deleted}, {modified]) """
    added = {} 
    deleted = {}
    modified = {}

    for i in range(len(dict2.keys())):
        key = dict2.keys()[i]
        value = dict2[key]
        if (not key in dict1.keys()):
            added[key] = value
        else:
            if (value[8] != dict1[key][8]):
                modified[key] = value
    for i in range(len(dict1.keys())):
        key = dict1.keys()[i]
        value = dict1[key]
        if (not key in dict2.keys()):
            deleted[key] = value
    return (added, deleted, modified)

def lstatfiles(filelist):
    """ Returns a dictionary {filename: lstat} for a given [filelist]. """
    statdict = {}
    for i in range(len(filelist)):
        statinfo = lstat(filelist[i])
        statdict[filelist[i]] = statinfo
    return statdict

def escapedfilename(filename):
    """ escapes special characters in filenames (currently "`") """
    filename = replace(filename, "`", "\`")
    return filename

def is_linux_kernel_2_6():
    try:
        uname_info = os.uname()
        os_name = uname_info[0]
        kernel_version = uname_info[2]
        if ((lower(os_name) == "linux") and (kernel_version[0:3] == "2.6")):
            return TRUE
        else:
            return FALSE
    except (AttributeError), detail:
        # os.uname() is not available on this architecture
        return FALSE

"""

Pipe functions

"""

def cmdoutput(command, strip = FALSE, waitpid = TRUE, returnerror = FALSE):
    """ Read the complete output of a command. """
    pipe = popen3(command)

    # os.wait is not available on the win32 platform so it is necessary to set this values
    if (sys.platform == "win32"):
        waitpid = FALSE

    if (returnerror == TRUE):
        output = pipe[2].readlines()
    else:
        output = pipe[0].readlines()

    if (strip == TRUE):
        output = striplist(output)

    if (pipe[0] != None):
        pipe[0].close()
    if (pipe[1] != None):
        pipe[1].close()
    if (pipe[2] != None):
        pipe[2].close()
    if (waitpid == TRUE):
        os.wait()
    del pipe
    pipe = None
    return output

def cmdexec(cmd):
    """ Executes a command in a subshell and returns (return_value, (stdout, stderr)). """

    if (sys.platform == "win32"):
        cmd = "(%s) 2>&1" % (cmd)
        result = 0
        stderr_output = []
        stdout_output = cmdoutput(cmd)
    else:
        my_popen3 = Popen3(cmd, True)

        # wait until the sub process has finished
        while (my_popen3.poll() == -1):
            sleep(0.01)

        stderr_output = my_popen3.fromchild.readlines()
        stdout_output = my_popen3.childerr.readlines()

        # read the result value
        result = my_popen3.poll()
        if (my_popen3.fromchild != None):
            my_popen3.fromchild.close()
        if (my_popen3.childerr != None):
            my_popen3.childerr.close()
        if (my_popen3.tochild != None):
            my_popen3.tochild.close()

    return (result, (stdout_output, stderr_output))

    
"""

General functions

"""

def SigChldHandler(signal_number, stack_frame):
    """ Handler, which waits for children to be closed. """

    # Reinstall the sigchild handler, because it gets deleted on libc5/sysv machines
    signal.signal(signal.SIGCHLD, SigChldHandler)
    pid = -1
    while (pid != 0):
        try:
            pid = os.waitpid(0, os.WNOHANG)[0]
        except:
            pid = 0

def ansi(text, fg = WHITE, bg = BLACK, bold = FALSE):
    """ ANSI text (fore- & background, bold font). """
    if (bold == TRUE):
        fg = "%s;1" % fg
    bg = str(atoi(bg) + 10)
    text = "\033[%s;%sm%s\033[0m" % (bg, fg, text)
    return text


"""

Extended version of urlparse (includes username & password)

"""

# extended urlparse function (including username, password)
# returns: <scheme>://<netloc>/<path>;<params>?<query>#<fragment>
# returns: <scheme>://<user>:<password>@<netloc>:<port>/<path>;<params>?<query>#<fragment>

urlparseorg = urlparse
_services_cache = {}

def readservices():
    global _services_cache
    services = {}
    if (len(_services_cache) == 0):
        if (os.path.exists("/etc/services")):
            file = open("/etc/services", "r")
            lines = file.readlines()
            file.close()
            for i in range(len(lines)):
                line = strip(lines[i])
                if (find(line, "#") != -1):
                    line = strip(line[:find(line, "#")])
                if (len(line) > 0):
                    nameportpair = split(line)
                    if (len(nameportpair) > 1):
                        name, port = nameportpair[:2]
                        if find(port, "/") != -1:
                            port, protocol = split(port, "/")
                            services[name] = port
        else:
            services["ftp"] = 21
            services["http"] = 80
            services["rsync"] = 873
        _services_cache = copy.copy(services)
    else:
        services = copy.copy(_services_cache)
    return services

def urlparse(url):
    rsync_found = FALSE
    if (url[0:5] == "rsync"):
        rsync_found = TRUE
        url = "ftp%s" % url[5:]
    loc_questionmark = find(url, "?")
    if (loc_questionmark != -1):
        loc_hash = find(url, "#", 0, loc_questionmark)
        while (loc_hash != -1):
            url = url[:loc_hash] + "'" + url[loc_hash + 1:]
            loc_hash = find(url, "#", 0, loc_questionmark)
    else:
        url = replace(url, "#", "'")

    scheme, netloc, path, params, query, fragment = urlparseorg(url)
    if (rsync_found):
        scheme = "rsync"
    services = readservices()
    user = password = ""
    if services.has_key(scheme):
        port = atoi(services[scheme])
    else:
        port = 0
    if (find(netloc, "@") != -1):
        user, netloc = split(netloc, "@")
    if (find(user, ":") != -1):
        user, password = split(user, ":")
    if (find(netloc, ":") != -1):
        netloc, port = split(netloc, ":")
        port = atoi(port)
    if (path == ""):
        path = "/"

    user = replace(user, "'", "#")
    password = replace(password, "'", "#")
    netloc = replace(netloc, "'", "#")
    path = replace(path, "'", "#")

    tuple = scheme, user, password, netloc, port, path, params, query, fragment

    return tuple

"""

Database functions

"""

def db_null_string(s):
    if (s == "") or (s == None):
        return "NULL"
    else:
        return s

"""

Miscellaneous functions

"""

def get_username():
    """ Returns the username of the current user. """
    if (environ.has_key("USER")):
        return environ["USER"]
    elif (environ.has_key("USERNAME")):
        return environ["USERNAME"]
    else:
        return "Unknown"

def get_tempdir():
    # Default directory on POSIX machines
    if ((environ.has_key("TMPDIR")) and (os.path.isdir(environ["TMPDIR"]))):
        return environ["TMPDIR"]
    # TEMP / TMP are for win32 systems
    elif ((environ.has_key("TEMP")) and (os.path.isdir(environ["TEMP"]))):
        return environ["TEMP"]
    elif ((environ.has_key("TMP")) and (os.path.isdir(environ["TMP"]))):
        return environ["TMP"]
    else:
        # Try to find another existing temporary directory
        if (os.path.exists("/tmp")):
            return "/tmp"
        elif (os.path.exists("/var/tmp")):
            return "/var/tmp"
        else:
            return "/usr/tmp"

"""

Wrapper class for gettext (works for all python versions)

"""

try:
    import gettext
    _gettext = gettext
    gettext_available = TRUE
except ImportError:
    gettext_available = FALSE

class gettext:

    def __init__(self, domain, localedir = None):
        """ Initialize the gettext wrapper. """
        if (gettext_available == TRUE):
            _gettext.bindtextdomain(domain, localedir)

    def install(self, domain, localedir = None):
        if (gettext_available == TRUE):
            _gettext.install(domain, localedir)

    def find(self, domain, localedir = None):
        if (gettext_available == TRUE):
            return _gettext.find(domain, localedir)
        else:
            return None

    def textdomain(self, domain = None):
        if (gettext_available == TRUE):
            return _gettext.textdomain(domain)
        else:
            return None

    def gettext(self, message):
        if (gettext_available == TRUE):
            return _gettext.gettext(message)
        else:
            return message

    def dgettext(self, domain, message):
        if (gettext_available == TRUE):
            return _gettext.dgettext(domain, message)
        else:
            return message

"""

Adaptive file locking

"""

class FileLock:

    # Status constants
    UNLOCKED = 0
    LOCKED_SELF = 1
    LOCKED_OTHER = 2
    ORPHAN = 3
    STALE = 4

    def __init__(self, filename, staletime = 43200):
        self.filename = filename
        self.ownerpid = None  # used to carry PID between status calls and actions
        self.staletime = staletime  # Default is 12 hours
        self.ps = process.ProcessTable()  # Process table for checking if PID lives

    def acquire(self):
        if (self.status() != FileLock.UNLOCKED):
            error("Already locked: %s" % self.filename)
            return FALSE

        debug("Acquiring lock: %s" % self.filename);

        try:
            file = open(self.filename, "w")
            file.write(str(getpid()))
            file.close()
        except IOError, msg:
            error("Failed to create lock file: %s (%s)" % (self.filename, msg))
            return FALSE

        return TRUE

    def release(self):
        if (self.status() != FileLock.LOCKED_SELF):
            error("Not locked or not owner: %s" % self.filename)
            return FALSE

        debug("Releasing lock: %s" % self.filename);

        try:
            unlink(self.filename)
        except IOError, msg:
            error("Failed to unlink lock file: %s (%s)" % (self.filename, msg))
            return FALSE

        return TRUE

    def refresh(self):
        if (self.status() != FileLock.LOCKED_SELF):
            error("Not owner: %s" % self.filename)
            return FALSE

        debug("Refreshing lock: %s" % self.filename);

        now = time()
        utime(self.filename, (now, now))
        
        return TRUE
    
    def killStaleLock(self):
        status = self.status()

        debug("Killing stale lock: %s" % self.filename);

        if (status == FileLock.ORPHAN):
            try:
                unlink(self.filename)
            except IOError, msg:
                error("Failed to unlink stale lock file: %s (%s)"
                                    % (self.filename, msg))
                return FALSE
            return TRUE
        elif (status == FileLock.STALE):
            try:
                unlink(self.filename)
            except IOError, msg:
                error("Failed to unlink stale lock file: %s (%s)"
                                    % (self.filename, msg))
                return FALSE
            try: 
                dead = FALSE
                kill(self.ownerpid, signal.SIGTERM)
                # Give it five minutes to die gracefully
                for tries in range(5):
                    time.sleep(60)
                    self.ps.read()
                    if (self.ps.process(atoi(self.ownerpid)) == None):
                        dead = TRUE
                        break
                if not dead:
                    # Use the *big* club
                    kill(self.ownerpid, signal.SIGKILL)
            except:
                error("Failed to kill stale lock owner process: %s" % self.ownerpid)
                return FALSE
            return TRUE
        else: 
            error("No lock, or not stale: %s" % self.filename)
            return FALSE

    def status(self):
        if (not os.path.exists(self.filename)):
            return FileLock.UNLOCKED

        self.ownerpid = None

        try:
            file = open(self.filename, "r")
            self.ownerpid = file.readline()
            file.close()
        except IOError, msg:
            error("Failed to read PID from lock file: %s (%s)"
                                % (self.filename, msg));
            # Assume its locked - perhaps owner didn't finish writing yet?
            return FileLock.LOCKED_OTHER

        # Does the current process own the lock?
        if (atoi(self.ownerpid) == getpid()):
            return FileLock.LOCKED_SELF
        
        # Determine if the lock file owner is alive
        self.ps.read()
        if (self.ps.process(atoi(self.ownerpid)) == None):
            return FileLock.ORPHAN

        # Determine if the lock is held by a hung process
        timestamp = os.path.getmtime(self.filename)
        now = time()
        if (now - timestamp > self.staletime):
            return FileLock.STALE

        # There is a valid process that is refreshing the lock file
        return FileLock.LOCKED_OTHER
