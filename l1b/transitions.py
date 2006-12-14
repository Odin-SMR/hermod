import MySQLdb
import os
import shutil
import sys
from hermod.hermodBase import *

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
            directory = os.path.dirname(i)
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
            os.symlink(self.destLOGfile,self.linkLOGfile)
        except OSError,inst:
            mesg = """Errormessage: "%s"
    ...while symlinking %s
        to %s\n""" % (str(inst),self.destLOGfile,self.linkLOGfile)
            sys.stderr.write(mesg)
            sys.excepthook(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
            
    def genStartScript(self,qsmr,qos):
        script = '''#!/usr/bin/python
#PBS -N id%0.2i.%0.4X.%s
#PBS -l walltime=%s,nice=19
#PBS -q new
#PBS -W QOS:%s

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
stdout.close()
stdin.close()
stderr.close()
sys.stdout.writelines(sout)
sys.stderr.writelines(serr)
command = 'ssh odinop@jet "readFreq %%0.4X %%i %%i %%i %%s"' %% (%i,%i,%i,%i,'%s') 
f,g,h=os.popen3(command)
sout = g.readlines()
sys.stdout.writelines(sout)
serr = h.readlines()
sys.stderr.writelines(serr)
f.close()
g.close()
h.close()
''' % (self.fqid,self.orbit,qsmr,self.maxproctime,qos,qsmr.replace('-','_'),self.name,self.orbit,self.orbit,self.calibration,self.freqmode,self.fqid,qsmr)
        return script

    def queue(self,qos):
        """
        Creates a python PBS-script to send into queue
        """
        cur = self.openDB.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("""select * from Versions where freqmode=%s and fqid=%s and active""",(self.freqmode,self.fqid))
        for i in cur:
            startscript = self.genStartScript(i['qsmr'],qos)
            os.chdir('/home/odinop/logs/')
            stdin,stdout = os.popen2("qsub")
            stdin.write(startscript)
            stdin.close()
            print stdout.readlines()
            stdout.close()
        cur.close()

    def forceQueue(self,qos,qsmr):
        startscript = self.genStartScript(qsmr,qos)
        os.chdir('/home/odinop/logs/')
        stdin,stdout = os.popen2("qsub")
        stdin.write(startscript)
        stdin.close()
        print stdout.readlines()
        stdout.close()

