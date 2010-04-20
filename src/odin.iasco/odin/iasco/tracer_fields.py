#!/usr/bin/python
# coding: UTF-8

import MySQLdb
from pymatlab.matlab import MatlabSession
import logging
import logging.config
import sys
import StringIO
from odin.config.environment import *

def hdfRead(date,orbit_list,fqid): 
    """
    Create mat-files (via matlab) of the orbit-files for one date and fqid at the time
    """
    logging.config.fileConfig("/home/zakrisso/hermod/src/odin.config/odin/config/odinlogger.cfg")
    logger = logging.getLogger("iasco_assimilate")
    
    backward = [] # Orbits that overlap the limit betweens two days, where the first part of the orbit doesn't belong to the date which is now being assmilated
    forward = [] # Orbits that overlap the limit betweens two days, where the last part of the orbit doesn't belong to the date which is now being assmilated
    # In the SMRhdf_read-files, these parts of the orbits that don't belong to the date are not used, only the part that belongs to the date that is now assimilated is used
    
    if orbit_list['start_utc'][0]<date:# orbit_list['start_utc'][0] corresponds to the start date of the first orbit of the date
        backward.append(orbit_list['orbit'][0])
    if date<orbit_list['stop_utc'][-1]:# orbit_list['stop_utc'][-1] corresponds to the end date of the last orbit of the date
        forward.append(orbit_list['orbit'][-1])

    # Executes SMR_501hdf_read and SMR_544hdf_read to create mat-files from the hdf-files
    if fqid==29:
        logger.info('Orbit process started in SMR_501hdf_read.m for date:',date,'fqid:',fqid,'and orbits',orbit_list['orbit'])  
        cmd = "addpath(genpath(" + config.get('GEM','MATLAB_DIR') + "));\n" + 'SMR_501hdf_read(' + str(orbit_list['orbit']) + ',' + str(backward) + ',' + str(forward) + ');'
    elif fqid==3:
        logger.info('Orbit process started in SMR_544hdf_read.m for date:',date,'fqid:',fqid,'and orbits',orbit_list['orbit'])
        cmd = "addpath(genpath(" + config.get('GEM','MATLAB_DIR') + "));\n" + 'SMR_544hdf_read(' + str(orbit_list['orbit']) + ',' + str(backward) + ',' + str(forward) + ');'
     
    session = MatlabSession('matlab -nodisplay') 
    session.putstring('command',cmd)
    
    try:
        session.run('eval(command)') 
    except RuntimeError as error_msg:
        logger.error(error_msg) # Write error to log
        session.close()
        raise(RuntimeError(error_msg))

    session.close()

    
