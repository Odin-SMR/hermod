import MySQLdb
import sys
import shutil
import os
import re

from datetime import datetime

from pyhdf.HDF import *
from pyhdf.VS import *
from hermod.hermodBase import *

def level2Factory(orbitNrDec,freqMode,calibration,fqid,version,db):
    if version == '2-1':
        return Level2(orbitNrDec,freqMode,calibration,fqid,version,db)
    elif version == '2-0':
        return Level2(orbitNrDec,freqMode,calibration,fqid,version,db)
    else:
        return None

class Level2:
    
    def __init__(self,orbitNrDec,freqMode,calibration,fqid,version,db):
        """
        The constructor that should be used
        """
        self.orbit = orbitNrDec
        self.freqmode = freqMode
        self.calibration = calibration
        self.fqid = fqid
        self.version = version
        self.db = db
        cursor = self.db.cursor(MySQLdb.cursors.DictCursor)
        status = cursor.execute('''select * from smr.level1 join odin.Freqmodes as freq using (backend) where orbit=%s and fqid=%s and calversion=%s''',(self.orbit,self.fqid,self.calibration))
        if status<>1:
            cursor.close()
            raise HermodWarning('Number of matches found: %s'%(status))
        else:
            res = cursor.fetchone()
            res['version'] = version
            res['l2version'] = version.replace('-','').zfill(3)
            self.info = res
        cursor.close()


    def setFileNames(self):
        level2template = os.path.join(config.get('GEM','SMRl2_DIR'),'%%s','Qsmr-%(version)s','%(name)s','SCH_%(midfreq)i_%(l2prefix)s%(orbit)0.4X_%(l2version)s.%%s') % self.info
        self.hdffile = level2template % ('SMRhdf','L2P')
        self.auxfile = level2template % ('SMRhdf','AUX')
        self.inffile = level2template % ('SMRhdf','ERR')
        self.matfile = level2template % ('SMRmat','mat')
        self.errfile = level2template % ('SMRmat','qsm_error')  

    def preClean(self):
        os.system("rm -f "+self.matfile)

                                                        
    def readData(self):
        """
        Reads a the associated hdf file. Returns a list of dictionaries. If an error occurs it returns an empty list.
        """
        table = "Geolocation"
        try:
            f = HDF(self.hdffile)                # open 'inventory.hdf' in read mode
            vs = f.vstart()                 # init vdata interface
            vd = vs.attach(table)   # attach 'INVENTORY' in read mode
            index = vd.inquire()[2]
            info = []
            a = iter(self.aux)
            for i in vd[:]:
                try:
                    data = a.next()
                    data.update(dict(zip(index,i)))
                except StopIteration:
                    pass
                data['date']= datetime(data.pop('Year'),data.pop('Month'),data.pop('Day'),data.pop('Hour'),data.pop('Min'),data.pop('Secs'),int(1000000*data.pop('Ticks')))
                data.update(self.info)
                info.append(data)
                
            self.geolocation = info
            vd.detach()               # "close" the vdata
            vs.end()                  # terminate the vdata interface
            f.close()                 # close the HDF file
        except HDF4Error,inst:
            mesg = "error reading %s: %s" % (self.hdffile,inst)
            raise HermodError(mesg)

    def addData(self):
        """
        Adds data into the odin database
        """
        c = self.db.cursor()
        c.execute('''delete from level2 where id=%(id)s and version2=%(version)s and fqid=%(fqid)s''',self.info)
        test = c.executemany("""INSERT level2 (processed,id,version2,latitude,longitude,mjd,date,sunZD,fqid,quality,p_offs,f_shift,chi2,chi2_y,chi2_x,marq_start,marq_stop,marq_min,n_iter,scanno) values (now(),%(id)s,%(version)s,%(Latitude)s,%(Longitude)s,%(MJD)s,%(date)s,%(SunZD)s,%(fqid)s,%(Quality)s,%(P_Offs)s,%(F_Shift)s,%(Chi2)s,%(Chi2_y)s,%(Chi2_x)s,%(Marq_Start)s,%(Marq_Stop)s,%(Marq_Min)s,%(N_Iter)s,%(ScanNo)s)""", (self.geolocation))
        c.close()
        return test
    
    def readAuxFile(self):
        data=[]
        typelist = [int,float,float,str,int,float,int,float,float,float,float,float,float,float,float,int]
        try:
            f = open(self.auxfile)
            versionnr = False
            headers = False
            if f.readline()[0] == '#':
                headers = True
            if f.readline()[0] == '#':
                versionnr = True
            f.seek(0)
            if versionnr:
                ver = f.readline().strip().split(' ')[1]
            if headers:
                head = f.readline()
                header = head.split()[1:]
            for line in f:
                    fields = line.split()
                    converted = [g(h) for g,h in zip(typelist,fields)]
                    data.append(dict(zip(header,converted))) 
        finally:
            f.close()
            self.aux = data

    def cleanFiles(self):
        """
        Removes matfiles and moves err-files
        """
        os.system("rm -f "+self.matfile)
        try:
            shutil.move(self.errfile,self.inffile)
        except IOError:
            mesg = "Couldn't move %s to %s" % (self.errfile,self.inffile)
            raise HermodError(mesg)

if __name__=="__main__":
    db = MySQLdb.connect(host=config.get('WRITE_SQL','host'), user=config.get('WRITE_SQL','user'), passwd=config.get('WRITE_SQL','passwd'), db='smr')
    x = Level2(0x8311,1,6,3,'2-0',db)
    x.setFileNames()
    x.readAuxFile()
    x.readData()
    x.addData()
