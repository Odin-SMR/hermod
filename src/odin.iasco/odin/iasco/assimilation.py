#!/usr/bin/python
# coding: UTF-8

from pymatlab.matlab import MatlabSession
from convert_date import utc2mjd
import logging
import logging.config
import sys
import StringIO
from odin.config.environment import *
from pkg_resources import resource_stream
from os.path import dirname

def assimilate(date,fqid): 
    """
    Run the assimilationprogram (via matlab) for the one date and fqid at the time
    """
    name = config().get('logging','configfile')
    file = resource_stream('odin.config',name)
    logging.config.fileConfig(file)
    root_logger = logging.getLogger("")
    logger = logging.getLogger("iasco_assimilate")
    file_dir = dirname(file.name)
    
    # Convert the date to mjd
    date_mjd=utc2mjd(date.year,date.month,date.day)
    
    # Define the species and levels    
    if fqid==29:
        species = ["'O3_501'","'N2O'"]       
        levels = ['[4 6 8 10]','[4 6 8 10]'] #corresponding to ['O3_501','N2O']
    if fqid==3:
        species = ["'O3_544'","'HNO3'","'H2O'"]       
        levels = ['[4 6 8 10]','[4 6 8 10 12 14]','[1 2 3 4 5 6]'] #corresponding to ['O3_544','HNO3','H2O']   
    
    session = MatlabSession('matlab -nodisplay')
    l=0    
    for spec in species:
        level = levels[l]
        logger.info('Running IASCO.m for date:',date,'levels: ' + level + ' and species:' + spec) # Write information to log
        cmd = "addpath(genpath('" + config().get('GEM','MATLAB_DIR') + "'), '" + file_dir + "');\n" + 'IASCO(' + str(date_mjd) + ',' + level + ',' + spec + ');'        
        session.putstring('command',cmd)
        try:
            session.run('eval(command)') 
        except RuntimeError as error_msg:
            logger.error(error_msg) # Write error to log
            session.close()
            raise(RuntimeError(error_msg))

        l=l+1        
    session.close()
