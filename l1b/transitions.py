import MySQLdb
import os
import shutil
import sys
from hermod.hermodBase import *
import subprocess as s

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
        self.linkHDFfile = "%sV-%i/%s/%s%0.4X.HDF" % (SMRL1B_DIR,self.calibration,self.name,self.prefix,self.orbit)
        self.linkLOGfile = "%sV-%i/%s/%s%0.4X.LOG" % (SMRL1B_DIR,self.calibration,self.name,self.prefix,self.orbit)

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
            
    def genStartScript(self,qsmr,queue):
        script = '''#!/usr/bin/python
#PBS -N id%0.2i.%0.4X.%s
#PBS -l walltime=%s,nice=19
#PBS -q %s

import os,sys
import subprocess as s
import MySQLdb as m
import tempfile as t

from hermod.l2.level2 import *

orbit=%i
freqmode=%i
fqid=%i
cal=%i
qsmr="%s"
name="%s"
dir=''
try:
    dir=t.mkdtemp()
except EnvironmentError,e:
    print >>sys.stderr "Hermod error:", e.errno ,e.strerror,e.filname
    print >>sys.stderr "              Couldn't create tempdir, trying to free diskspace.."
    status = os.command('find /tmp -maxdepth 1 -user odinop -mmin +600 -name "Tmp*" -exec rm -rf \{\} \;')
    dir = t.mkdtemp()

matlab = s.Popen(['matlab','-nojvm','-nosplash'],stdout=s.PIPE,stdin=s.PIPE,stderr=s.PIPE)

command = """cd /home/odinop/Matlab/Qsmr_%%s
set(gcf,'Visible','off');
path(path,'~');
qsmr_startup;
qsmr_inv_op('%%s','%%0.4X','%%0.4X','%%s')
close all
clear all
clear all
quit
""" %% (qsmr.replace('-','_'),name,orbit,orbit,dir)

out = matlab.communicate(input=command)

sys.stdout.write(out[0])
sys.stderr.write(out[1])

print "Hermod info: Matlab closed with statuscode:",matlab.returncode

try:
    retcode = s.call("rm -rf " + dir, shell=True)
    if retcode != 0:
        print >>sys.stderr, "Hermod error: rm -rf",dir,"returned:", retcode
except OSError, e:
    print >>sys.stderr,     "Hermod error:", e.errno, e.strerror, e.filename

db = MySQLdb.connect(host=config.get('WRITE_SQL','host'), user=config.get('WRITE_SQL','user'), passwd=config.get('WRITE_SQL','passwd'), db=config.get('WRITE_SQL','db'))

l2p = Level2(orbit,freqmode,cal,fqid,qsmr,db)

status = os.system('rm -f '+l2p.matfile)
print """
Trying to find L2P-file to add information into the database.
Orbit %%0.4X mode %%i in calibration %%i in version %%s and fqid %%i
""" %% (orbit,freqmode,cal,qsmr,fqid)
l2p.dell2()
try:
    l2p.readl2()
except HermodError,inst:
    sys.stderr.write(str(inst))
    msg="Probably no L2P-file produced\\n"
    sys.stderr.write(msg)
    print msg 
    try:
        l2p.cleanFiles()
    except HermodError,inst:
        sys.stderr.write(str(inst))
    db.close()
    sys.exit(1)
l2p.addData()
l2p.cleanFiles()
db.close()

''' % (self.fqid,self.orbit,qsmr,self.maxproctime,queue,self.orbit,self.freqmode,self.fqid,self.calibration,qsmr,self.name)
        return script

    def queue(self,queue):
        """
        Creates a python PBS-script to send into queue
        """
        cur = self.openDB.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("""select * from Versions where freqmode=%s and fqid=%s and active""",(self.freqmode,self.fqid))
        for i in cur:
            startscript = self.genStartScript(i['qsmr'],queue)
            x = s.Popen("qsub",stdin=s.PIPE,stdout=s.PIPE,stderr=s.PIPE,cwd='/home/odinop/logs/')
            out = x.communicate(input=startscript)
            print out[0]
            sys.stderr.write(out[1])
        cur.close()

    def forceQueue(self,queue,qsmr):
        startscript = self.genStartScript(qsmr,queue)
        x = s.Popen("qsub",stdin=s.PIPE,stdout=s.PIPE,stderr=s.PIPE,cwd='/home/odinop/logs/')
        out = x.communicate(input=startscript)
        print out[0]
        sys.stderr.write(out[1])

