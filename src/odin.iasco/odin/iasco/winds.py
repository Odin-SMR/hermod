#!/usr/bin/python
# coding: UTF-8

import os.path
import shutil
import sys
import StringIO
import logging
import logging.config
from pymatlab.matlab import MatlabSession
from convert_date import utc2mjd
from datetime import timedelta
from odin.config.environment import *

def extractWinds(date): 
    """
    Extraction of the wind-files via matlab
    """
    logging.config.fileConfig("logging.conf")
    logger = logging.getLogger("iasco_winds")
    
    logger.info('Extracting winds in MakeWinds.m for date:',date) #Write information to log
    # Convert the date to mjd
    date_mjd=utc2mjd(date.year,date.month,date.day)

    cmd = "addpath(genpath(" + config.get('GEM','MATLAB_DIR') + "));\n" + 'MakeWinds(' + str(date_mjd) + ');' 
    session = MatlabSession('matlab -nodisplay') 
    session.putstring('command',cmd)
        
    try:
        session.run('eval(command)') 
    except RuntimeError as error_msg:
        logger.error(error_msg) # Write error to log
        session.close()
        raise(RuntimeError(error_msg))

    session.close()

def copyWinds(date): 
    """
    Copy existing wind-files if there are no extracted wind-files for the specific day and/or time and/or level
    """
    logging.config.fileConfig("logging.conf")
    logger = logging.getLogger("iasco_winds")
    
    path=config.get('GEM','WIND2_DIR') ### Path to the wind data
    year,month,day=date.year,date.month,date.day
    year,month,day='%02d' %(year-2000),'%02d' %(month),'%02d' %(day)
        
    for k in range(400,1025,25): ### The potential temperature levels for the wind data
        for j in [0,6,12,18]: ### The time of the day for the wind data
            wanted_file = path + str(year) + '/' + str(month) + '/' + 'winds2_' + str(year) + str(month) + str(day) + '.' + str(j) + '.' + str(k) + '.mat' 
            if not os.path.exists(wanted_file): ### If the wanted file doesn't exist, the file before is copied and used instead of the missing file 
                if j==0: ### If j=0 the file before is on at least on day before
                    date_0=date
                    copy_file = path + str(year) + '/' + str(month) + '/' + 'winds2_' + str(year) + str(month) + str(day) + '.' + str(j) + '.' + str(k) + '.mat'
                    while not os.path.exists(copy_file):
                        date_0 = date_0-timedelta(1)
                        year_c,month_c,day_c=date_0.year,date_0.month,date_0.day
                        year_c,month_c,day_c='%02d' %(year_c-2000),'%02d' %(month_c),'%02d' %(day_c)
                        for time in [18,12,6,0]: ### If there isn't wind data from the day before to copy, we iterate days and times until we find data. We start with time=18 to make sure the data we find is the closest before the j=0 data we are missing 
                            copy_file = path + str(year_c) + '/' + str(month_c) + '/' + 'winds2_' + str(year_c) + str(month_c) + str(day_c) + '.' + str(time) + '.' + str(k) + '.mat'
                            if os.path.exists(copy_file):
                                if not os.path.exists(path + str(year) + '/'):
                                    os.mkdir(path + str(year) + '/')
                                if not os.path.exists(path + str(year) + '/' + str(month) + '/'):
                                    os.mkdir(path + str(year) + '/' + str(month) + '/')
                                shutil.copyfile(copy_file,wanted_file)
                                logger.info(wanted_file,'were missed so',copy_file,'was copied') # Information to log
                                break
            
                else: ### If wind data is missing for j=6,12,18 we just copy from the same day, 6h before, because we can be sure we have data for time=0 on the actual day(the code above)
                    copy_file = path + str(year) + '/' + str(month) + '/' + 'winds2_' + str(year) + str(month) + str(day) + '.' + str(j-6) + '.' + str(k) + '.mat'
                    if not os.path.exists(path + str(year) + '/'):
                        os.mkdir(path + str(year) + '/')
                    if not os.path.exists(path + str(year) + '/' + str(month) + '/'):
                        os.mkdir(path + str(year) + '/' + str(month) + '/')
                    shutil.copyfile(copy_file,wanted_file)
                    logger.info(wanted_file,'were missed so',copy_file,'was copied') # Information to log
