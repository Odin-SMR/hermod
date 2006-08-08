import insertFiles
import MySQLdb
import os
import shutil
import sys

#Set path
SPOOL_DIR= "/odin/smr/Data/spool"
FAILURE_DIR="/odin/smr/Data/spool_failure"
MISSING_LOG="/odin/smr/Data/spool_missing"
LEVEL1B_DIR= "/odin/smr/Data/level1b"
SMRL1B_DIR="/odin/smr/Data/SMRl1b"



class Transition:
    
    def __init__(self,dbrow,level1bObject):
        self.maxproctime = dbrow['maxproctime']
        self.l2prefix = dbrow['l2prefix']
        self.midfreq = dbrow['midfreq']
        self.backend = dbrow['backend']
        self.freqmode = dbrow['freqmode']
        self.prefix = dbrow['prefix']
        self.name = dbrow['name']
        self.fqid = dbrow['fqid']
        self.openDB = level1bObject.openDB
        self.origHDFfile = level1bObject.origHDFfile
        self.origLOGfile = level1bObject.origLOGfile
        self.destHDFfile = level1bObject.destHDFfile
        self.destLOGfile = level1bObject.destLOGfile
        self.destZPTfile = level1bObject.destZPTfile
        self.linkZPTfile = level1bObject.linkZPTfile
        self.calibration = level1bObject.calibration
        self.orbit       = level1bObject.orbit
        self.createNames()

    def createNames(self):
        self.linkHDFfile = "%s/V-%i/%s/%s%0.4X.HDF" % (SMRL1B_DIR,self.calibration,self.name,self.prefix,self.orbit)
        self.linkLOGfile = "%s/V-%i/%s/%s%0.4X.LOG" % (SMRL1B_DIR,self.calibration,self.name,self.prefix,self.orbit)

        self.files = [self.linkHDFfile, self.linkLOGfile,]

    def createDirectories(self):
        for i in self.files:
            directory = os.path.basename(i)
            if os.path.exists(directory):
                pass
            else:
                try:
                    os.makedirs(directory)
                except OSError,inst:
                    mesg = """Errormessage: "%s"\n
    ...while makeing directory %s""" % (str(inst),directory)
                    sys.stderr.write(mesg)
                    sys.excepthook(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])

    def createLink(self):
        """
        removes old link and creates the new one
        """
        try:
            os.remove(self.linkHDFfile)
        except OSError:
            pass
        try:    
            os.symlink(self.destHDFfile,self.linkHDFfile)
        except OSError,inst:
            mesg = """Errormessage: "%s"
    ...while symlinking %s
        to %s\n""" % (str(inst),self.destHDFfile,self.linkHDFfile)
            sys.stderr.write(mesg)
            sys.excepthook(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
        try:
            os.remove(self.linkLOGfile)
        except OSError:
            pass
         try:    
            os.symlink(self.destLOFfile,self.linkLOGfile)
        except OSError,inst:
            mesg = """Errormessage: "%s"
    ...while symlinking %s
        to %s\n""" % (str(inst),self.destLOGfile,self.linkLOGfile)
            sys.stderr.write(mesg)
            sys.excepthook(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
            
    def queue(self):
        """
        Creates a python PBS-script to send into queue
        """
        cur = self.openDB.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("""select * from Versions where freqmode=%s and fqid=%s and active""",(self.freqmode,self.fqid))
        for i in cur:
            startscript = '''#!/usr/bin/python
#PBS -N %0.2i_%0.4X_%s
#PBS -l walltime=%s,nice=19
#PBS -Z
#PBS -V
#PBS_O_WORKDIR /home/odinop/logs

import os,sys

matlab_command = """matlab -nojvm << end_tag
cd /home/odinop/Matlab/Qsmr_%%s
set(gcf,'Visible','off');
path(path,'~');
qsmr_startup;
qsmr_inv_op('%%s','%%0.4X')
close all
clear all
clear all
quit
end_tag

""" %% ('%s','%s',%i)
stdin,stdout,stderr = os.popen3(matlab_command)
sout = stdout.readlines()
serr = stderr.readlines()
sys.stdout.writelines(sout)
sys.stderr.writelines(serr)
command = 'ssh odinop@jet "/home/odinop/hermod/l2/readFreq.py %%0.4X %%i %%i %%i %%s' %% (%i,%i,%i,%i,'%s') 
status=os.system(command)
''' % (self.fqid,self.orbit,i['qsmr'],self.maxproctime,i['qsmr'],self.name,self.orbit,self.orbit,self.calibration,self.freqmode,self.fqid,i['qsmr'])
            print startscript
        cur.close()
