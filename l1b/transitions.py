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

    def queue(self,queue):
        """
        Creates a python PBS-script to send into queue
        """
        cur = self.openDB.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("""select * from Versions where freqmode=%s and fqid=%s and active""",(self.freqmode,self.fqid))
        for i in cur:
            name = 'id%0.2i.%0.4X.%s' %(self.fqid,self.orbit,i['qsmr'])
            launch =['/usr/bin/qsub','-N%s' %(name),'-lwalltime=%s,nice=19' % (self.maxproctime),'-q%s' %(queue),'-vORBIT=%i,FREQMODE=%i,CALIBRATION=%i,FQID=%i,NAME=%s,QSMR=%s'%(self.orbit,self.freqmode,self.calibration,self.fqid,self.name,i['qsmr']),'-e%s%s.err'%(config.get('GEM','logs'),name),'-o%s%s.out'%(config.get('GEM','logs'),name),'/usr/bin/hermodrunjob']
            x = s.Popen(launch,stdin=s.PIPE,stdout=s.PIPE,stderr=s.PIPE)
            x.stdin.close()
            status = x.wait()
            print 'exit status:',status
        cur.close()

    def forceQueue(self,queue,qsmr):
        name = 'id%0.2i.%0.4X.%s' %(self.fqid,self.orbit,qsmr)
        launch =['/usr/bin/qsub','-N%s' %(name),'-lwalltime=%s,nice=19' % (self.maxproctime),'-q%s' %(queue),'-vORBIT=%i,FREQMODE=%i,CALIBRATION=%i,FQID=%i,NAME=%s,QSMR=%s'%(self.orbit,self.freqmode,self.calibration,self.fqid,self.name,qsmr),'-e%s%s.err'%(config.get('GEM','logs'),name),'-o%s%s.out'%(config.get('GEM','logs'),name),'/usr/bin/hermodrunjob']
        x = s.Popen(launch,stdin=s.PIPE,stdout=s.PIPE,stderr=s.PIPE)
        x.stdin.close()
        status = x.wait()
        print 'exit status:',status

