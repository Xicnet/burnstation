import logging
import  LoadConfig
config = LoadConfig.LoadConfig()

verbosity = 5

class MyLogger:
    def __init__(self, file=None, format=None):

        self.InitAll(file, format)

    def InitAll(self, file=None, format=None):
        self.SetFile(file)
        self.CreateLogger()
        self.SetFormat(format)

    def SetFile(self, file):
        # define the log file
        if file is None: file = 'Main.log'

        self.logfile = config.logPath + '/' + file

    def CreateLogger(self):
        self.logger = logging.getLogger('Burnstation')
        self.handler = logging.FileHandler(self.logfile)

    def SetFormat(self, format=None):
        if format is None: format = '%(asctime)s %(levelname)s %(message)s'

        formatter = logging.Formatter(format)
        self.handler.setFormatter(formatter)

        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)

	self.info("MyLogger 2.0 started....!")

    def log(self, level, s):
        if ( level == 1 ) and ( verbosity > 0 ):
            try: self.logger.debug('(%i) %s' % (level, s))
            except Exception, e: print "DEBUG1: exception ocurred trying to log :" + str(e)
        if ( level == 2 ) and ( verbosity > 1 ):
            try: self.logger.debug('(%i) %s' % (level, s))
            except Exception, e: print "DEBUG2: exception ocurred trying to log :" + str(e)
        if ( level == 3 ) and ( verbosity > 2 ):
            try: self.logger.debug('(%i) %s' % (level, s))
            except Exception, e: print "DEBUG3: exception ocurred trying to log :" + str(e)
        if ( level == 4 ) and ( verbosity > 3 ):
            try: self.logger.debug('(%i) %s' % (level, s))
            except Exception, e: print "DEBUG4: exception ocurred trying to log :" + str(e)
        if ( level == 5 ) and ( verbosity > 4 ):
            try: self.logger.debug('(%i) %s' % (level, s))
            except Exception, e: print "DEBUG5: exception ocurred trying to log :" + str(e)
        if ( level == 99 ) and ( verbosity > 5 ):
            try: self.logger.debug('(%i) %s' % (level, s))
            except Exception, e: print "DEBUG99: exception ocurred trying to log :" + str(e)

    def stdout(self, s):
        self.logger.info("(stdout)" + s)

    def debug(self, s):
        self.log(1, s)

    def debug1(self, s):
        self.log(1, s)

    def debug2(self, s):
        self.log(2, s)

    def debug3(self, s):
        self.log(3, s)

    def debug4(self, s):
        self.log(4, s)

    def debug5(self, s):
        self.log(5, s)

    def debug99(self, s):
        self.log(99, s)

    def warn(self, s):
        self.logger.warn(s)

    def info(self, s):
        self.logger.info(s)

    def error(self, s):
        self.logger.error(s)

    def exception(self, s):
        self.logger.exception(s)

logger = MyLogger()

#--------------------------------------------------------------------------------
# Exceptions and stderr handler
import traceback, datetime, sys, string

def myExceptHook(type, value, tb):
    sys.__excepthook__(type, value, tb)
    lines = traceback.format_exception(type, value, tb)

    exception = string.join(lines)
    
    start      = "----------------- START CUT HERE ----------------\n"
    timestamp  = "Timestamp: " + str( datetime.datetime.now() ) + "\n"
    end        = "----------------- END CUT HERE ------------------"

    logger.error(start + timestamp + exception)
    logger.error(end)

sys.excepthook = myExceptHook

#-------------------------------------------
class StderrFaker:
    def write(self, message):
        #message = message.strip() 
        #print "MyStdErr: " + message
        pass

#sys.stderr = StderrFaker()
#-------------------------------------------
'''
class StdoutFaker:
    def write(self, message):
        message = message.strip() 
        print "MyStdOut: " + message
        #logger.error(end)

sys.stdout = StdoutFaker()
'''
#-------------------------------------------
class Redirect:
    def __init__(self, stdout, save=True):
        self.save = save
        self.stdout = stdout

    def write(self, s):
        #self.stdout.write(string.lower(s))
        if self.save == True: logger.info("(stdout) "+s.strip())

#sys.stdout = Redirect(sys.stdout)
#-------------------------------------------

