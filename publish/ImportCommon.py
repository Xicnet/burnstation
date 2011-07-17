#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
A very simple log/debugging system
'''

verbosity = 99

def myLogger(msg, level, verbosity):
    '''
    My temporary logger system.
    '''

    if ( level == 1 ) and ( verbosity > 0 ):
        try: print "DEBUG1: " + msg
        except Exception, e: print "DEBUG1: ERROR: the following exception ocurred trying to pring debug info: :" + str(e)
    if ( level == 2 ) and ( verbosity > 1 ):
        try: print "DEBUG2: " + msg
        except Exception, e: print "DEBUG2: ERROR: the following exception ocurred trying to pring debug info: :" + str(e)
    if ( level == 3 ) and ( verbosity > 2 ):
        try: print "DEBUG3: " + msg
        except Exception, e: print "DEBUG3: ERROR: the following exception ocurred trying to pring debug info: :" + str(e)
    if ( level == 4 ) and ( verbosity > 3 ):
        try: print "DEBUG4: " + msg
        except Exception, e: print "DEBUG4: ERROR: the following exception ocurred trying to pring debug info: :" + str(e)
    if ( level == 5 ) and ( verbosity > 4 ):
        try: print "DEBUG5: " + msg
        except Exception, e: print "DEBUG5: ERROR: the following exception ocurred trying to pring debug info: :" + str(e)
    if ( level == 99 ) and ( verbosity > 98 ):
        try: print "DEBUG99: " + msg
        except Exception, e: print "DEBUG99: ERROR: the following exception ocurred trying to pring debug info: :" + str(e)

def debug1(msg):
    myLogger(msg, 1, verbosity)

def debug2(msg):
    myLogger(msg, 2, verbosity)

def debug3(msg):
    myLogger(msg, 3, verbosity)

def debug4(msg):
    myLogger(msg, 4, verbosity)

def debug5(msg):
    myLogger(msg, 5, verbosity)

def debug99(msg):
    myLogger(msg, 99, verbosity)

