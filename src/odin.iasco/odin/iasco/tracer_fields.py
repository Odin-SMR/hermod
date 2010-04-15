#!/usr/bin/python
# coding: UTF-8

import MySQLdb
from pymatlab.matlab import MatlabSession
#from odin.hermod.session import matlab
import sys
import StringIO

def hdfRead(date,orbit_list,fqid): 
    """
    Create mat-files (via matlab) of the orbit-files for one date and fqid at the time
    """
    backward = [] # Orbits that overlap the limit betweens two days, where the first part of the orbit doesn't belong to the date which is now being assmilated
    forward = [] # Orbits that overlap the limit betweens two days, where the last part of the orbit doesn't belong to the date which is now being assmilated
    # In the SMRhdf_read-files, these parts of the orbits that don't belong to the date are not used, only the part that belongs to the date that is now assimilated is used
    
    if orbit_list['start_utc'][0]<date:# orbit_list['start_utc'][0] corresponds to the start date of the first orbit of the date
        backward.append(orbit_list['orbit'][0])
    if date<orbit_list['stop_utc'][-1]:# orbit_list['stop_utc'][-1] corresponds to the end date of the last orbit of the date
        forward.append(orbit_list['orbit'][-1])

    # Executes SMR_501hdf_read and SMR_544hdf_read to create mat-files from the hdf-files
    if fqid==29:
        cmd = "addpath(genpath('/home/odinop/Matlab/IASCO_matlab-rev423/'));\n"
              'SMR_501hdf_read(' + str(orbit_list['orbit']) + ',' + str(backward) + ',' + str(forward) + ');'
    elif fqid==3:
        cmd = "addpath(genpath('/home/odinop/Matlab/IASCO_matlab-rev423/'));\n"
              'SMR_544hdf_read(' + str(orbit_list['orbit']) + ',' + str(backward) + ',' + str(forward) + ');'
     
    session = MatlabSession() #OPTIONS
    session.putstring('command',cmd)
    errorMess = session.run('eval(command)') 
    session.close()
    
    if not errorMess=='':
        sys.exit(errorMess + '\nDate = ' + str(date))
    
    #err=StringIO.StringIO()
    #a = matlab(errorFile=err)
    #cmds = []
    #cmds.append("addpath(genpath('/home/odinop/Matlab/IASCO_matlab-rev423/'))")
    #if fqid==29:
    #    cmds.append('SMR_501hdf_read(' + str(orbit_list['orbit']) + ',' + str(backward) + ',' + str(forward) + ')')
    #elif fqid==3:
    #    cmds.append('SMR_544hdf_read(' + str(orbit_list['orbit']) + ',' + str(backward) + ',' + str(forward) + ')')
    #a.commands(cmds)
    #a.close()
    #errors = err.getvalue()
    #if not errors=='':
    #    sys.exit(errors + '\nDate = ' + str(date))
    #err.close()
