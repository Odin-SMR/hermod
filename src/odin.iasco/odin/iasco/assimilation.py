#!/usr/bin/python
# coding: UTF-8

from pymatlab.matlab import MatlabSession
from convert_date import utc2mjd
import sys
import StringIO
from odin.config.config import *

def assimilate(date,fqid): 
    """
    Run the assimilationprogram (via matlab) for the one date and fqid at the time
    """
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
        print 'Running IASCO.m for date:',date,'levels: ' + level + ' and species:' + spec
        cmd = 'addpath(genpath(' + config.get('GEM','MATLAB_DIR') + '));\n' + 'IASCO(' + str(date_mjd) + ',' + level + ',' + spec + ');'        
        session.putstring('command',cmd)
        try:
            session.run('eval(command)') 
        except RuntimeError as error_msg
            print 'This into logg!!!!!!', error_msg
            session.close()
            raise(RuntimeError(error_msg))

        l=l+1        
    session.close()
