#!/usr/bin/python
# coding: UTF-8

#from odin.hermod.session import matlab
from pymatlab.matlab import MatlabSession
from convert_date import utc2mjd
import sys
import StringIO

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
    
    l=0    
    for spec in species:
        level = levels[l]
        cmd = "addpath(genpath('/home/odinop/Matlab/IASCO_matlab-rev423/'));\n"
              'IASCO(' + str(date_mjd) + ',' + level + ',' + spec + ');'
        session = MatlabSession() #OPTIONS
        session.putstring('command',cmd)
        errorMess = session.run('eval(command)') 
        session.close()
        
        if not errorMess=='':
            sys.exit(errorMess + '\nDate = ' + str(date))
        
        #err=StringIO.StringIO()
        #a = matlab(errorFile=err)
        #level = levels[l]
        #cmds = []
        #cmds.append("addpath(genpath('/home/odinop/Matlab/IASCO_matlab-rev423/'))")
        #cmds.append('IASCO(' + str(date_mjd) + ',' + level + ',' + spec + ')')
        #a.commands(cmds)
        #a.close()
        #errors = err.getvalue()
        #if not errors=='':
        #    sys.exit(errors + '\nDate = ' + str(date))
        #err.close()
        l=l+1
