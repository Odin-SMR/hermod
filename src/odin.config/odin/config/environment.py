from ConfigParser import SafeConfigParser
from os.path import expanduser
from os import stat
from stat import S_IMODE,S_IRGRP,ST_MODE,S_IROTH
from pkg_resources import resource_stream
class HermodError(Exception):
    pass

class HermodWarning(Exception):
    pass

def config():
    t = SafeConfigParser()
    defaults = resource_stream("odin","defaults.conf")
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


    
