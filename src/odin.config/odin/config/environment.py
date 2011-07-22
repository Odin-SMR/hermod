from ConfigParser import SafeConfigParser
from os.path import expanduser
from os import stat
from sys import stdout
from stat import S_IMODE,S_IRGRP,ST_MODE,S_IROTH
from pkg_resources import resource_filename
import logging
import logging.config
from tempfile import NamedTemporaryFile
class HermodError(Exception):
    pass

class HermodWarning(Exception):
    pass

def config():
    log = logging.getLogger(__name__)
    t = SafeConfigParser()
    config_files = t.read([
    	resource_filename("odin.config","defaults.cfg"),
        expanduser('~/.hermod.cfg'),
        expanduser('~/.hermod.cfg.secret'),
        ])
    log.debug("Using configfiles {0} latest one overrides".format(
            " ".join(config_files)))
    if expanduser('~/.hermod.cfg.secret') not in config_files:
        mesg = " ".join ("Make sure to create a file called",
                expanduser('~/.hermod.cfg.secret'),
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

def set_hermod_logging():
    parser = SafeConfigParser()
    used_files = parser.read([
            resource_filename('odin.config','odinlogger.cfg'),
            expanduser('~/.hermod.logger.cfg'), 
            ])
    # create a temporary file on disk
    config_file = NamedTemporaryFile()
    parser.write(config_file)
    config_file.file.flush()
    # let the logger read the temporary file
    logging.config.fileConfig(config_file.name)
    
