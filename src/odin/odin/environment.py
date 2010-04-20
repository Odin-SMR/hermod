from ConfigParser import SafeConfigParser
from logging.handler import TimedRotationFileHandler
from logging import getLogger,DEBUG,INFO,WARNING,ERROR,CRITICAL
from os.path import expanduser
from os import stat
from stat import S_IMODE,S_IRGRP,ST_MODE,S_ROTH

class HermodError(Exception):
    pass

class HermodWarning(Exception):
    pass

def config():
    t = safeConfigParser()
    defaults = resource_stream(__name__,"defaults.conf")
    t.readfp(defaults)
    config_files = t.read([
        expanduser('~/.hermod.cfg'),
        expanduser('~/.hermod.cfg.secret'),
        ])
    if expanduser('~/.hermod.cfg.secret') not in config_files:
        mesg = " ".join ("Make sure to create a file called",
                os.path.expanduser('~/.hermod.cfg.secret'),
                "and put your passwords in it.",
                "protect it with read permissions only for you")
        raise HermodError(mesg)
    else:
    # check for permissions of secret config files
        if S_IMODE(stat(expanduser('~/.hermod.cfg.secret'))[ST_MODE])&S_IRGRP:
            mesg ="Set not readable for group on ~/.hermod.cfg.secret"
            raise HermodError(mesg)
        if S_IMODE(stat(expanduser('~/.hermod.cfg.secret'))[ST_MODE])&S_IROTH:
            mesg ="set not readable for other on ~/.hermod.cfg.secret"
            raise HermodError(mesg)
    return t

def logger():
    conf = config()
    rootLogger = getLogger('')
    rootLogger.setLevel(eval(conf.get('logging','level')))
    rootLogger.addHandler(TimedRotationFileHandler(
        conf.get('logging','logfile'),when='D',intervall='30'))

    
