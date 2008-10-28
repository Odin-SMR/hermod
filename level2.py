import MySQLdb
import sys
import shutil
import os
import re

from datetime import datetime

from pyhdf.HDF import * 
from pyhdf.VS import *

from hermod.pdc import connection
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
        hdftemplate = os.path.join(config.get('GEM','SMRl2_DIR'),'SMRhdf','Qsmr-%(version)s','%(name)s','SCH_%(midfreq)i_%(l2prefix)s%(orbit)0.4X_%(l2version)s.%%s') % self.info
        mattemplate = os.path.join(config.get('GEM','SMRl2_DIR'),'SMRmat','Qsmr-%(version)s','%(name)s','%(prefix)s%(orbit)0.4X.%%s') % self.info
        self.hdffile = hdftemplate % ('L2P')
        self.auxfile = hdftemplate % ('AUX')
        self.inffile = hdftemplate % ('ERR')
        self.matfile = mattemplate % ('mat')
        self.errfile = mattemplate % ('qsmr_error')  
        self.pdcfile = os.path.join(config.get('PDC','SMRl2_DIR'),'version_%s'%(self.version.replace('-','.')),'%(name)s','SCH_%(midfreq)i_%(l2prefix)s%(orbit)0.4X_%(l2version)s.L2P') % self.info

    def preClean(self):
        print "removing old matfile: %s" % self.matfile
        print "removing old l2pfile: %s" % self.hdffile
        os.system("rm -f "+self.matfile)
        os.system("rm -f "+self.hdffile)

                                                        
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
        self.pscans=len(self.geolocation)

    def addData(self):
        """
        Adds data into the odin database
        """
        c = self.db.cursor()
        c.execute('''delete from level2files where id=%(id)s and version=%(version)s and fqid=%(fqid)s''',self.info)
        c.execute('''delete from level2 where id=%(id)s and version2=%(version)s and fqid=%(fqid)s''',self.info)
        c.execute('''INSERT level2files (id,fqid,version,nscans,verstr,hdfname,pdcname,processed) values (%s,%s,%s,%s,%s,%s,%s,now())''',(self.info['id'],self.fqid,self.version,self.pscans,self.verstr,self.hdffile.split(config.get('GEM','smrl2_dir'))[1],self.pdcfile.split(config.get('PDC','smrl2_dir'))[1]))
	for i in self.geolocation:
	   test = c.execute ("""INSERT level2 (id,version2,latitude,longitude,mjd,date,sunZD,fqid,quality,p_offs,f_shift,chi2,chi2_y,chi2_x,marq_start,marq_stop,marq_min,n_iter,scanno) values (%(id)s,%(version)s,%(Latitude)s,%(Longitude)s,%(MJD)s,%(date)s,%(SunZD)s,%(fqid)s,%(Quality)s,%(P_Offs)s,%(F_Shift)s,%(Chi2)s,%(Chi2_y)s,%(Chi2_x)s,%(Marq_Start)s,%(Marq_Stop)s,%(Marq_Min)s,%(N_Iter)s,%(ScanNo)s)""", i)

#        test = c.executemany("""INSERT level2 (id,version2,latitude,longitude,mjd,date,sunZD,fqid,quality,p_offs,f_shift,chi2,chi2_y,chi2_x,marq_start,marq_stop,marq_min,n_iter,scanno) values (%(id)s,%(version)s,%(Latitude)s,%(Longitude)s,%(MJD)s,%(date)s,%(SunZD)s,%(fqid)s,%(Quality)s,%(P_Offs)s,%(F_Shift)s,%(Chi2)s,%(Chi2_y)s,%(Chi2_x)s,%(Marq_Start)s,%(Marq_Stop)s,%(Marq_Min)s,%(N_Iter)s,%(ScanNo)s)""", self.geolocation)
        c.close()
        return test
    
    def readAuxFile(self):
        data=[]
        typelist = [int,float,float,str,int,float,int,float,float,float,float,float,float,float,float,int]
        #print "reading auxfile: %s" % self.auxfile
        try:
            f = open(self.auxfile)
        except:
            raise HermodError('No auxfile found %s'%(self.auxfile))
        try:
            versionnr = False
            headers = False
            if f.readline()[0] == '#':
                headers = True
            if f.readline()[0] == '#':
                versionnr = True
            f.seek(0)
            if versionnr:
                ver = f.readline().strip().split(' ')[1]
            else:
                ver = None
            if headers:
                head = f.readline()
                header = head.split()[1:]
            for line in f:
                    fields = line.split()
                    converted = [g(h) for g,h in zip(typelist,fields)]
                    map = dict(zip(header,converted))
                    map['ver'] = ver
                    data.append(map) 
        finally:
            f.close()
            self.verstr = ver
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

    def upload(self):
        c = self.db.cursor()
        status = c.execute('''select upload from odin.Versions where calibration=%s and qsmr=%s and freqmode=%s and fqid=%s''',(self.calibration,self.version,self.freqmode,self.fqid))
        if status ==1:
            if c.fetchone()[0]==1:
                uploadpairs = [(self.hdffile,self.pdcfile)]
                try:
                    con = connection()
                    con.uploads(uploadpairs)
                except HermodError, inst:
                    raise HermodError('Error while uploading: %s'%(inst)) 
                c.execute('''update level2files set uploaded=now() where id=%(id)s''',self.info)

        elif status >1:
            raise HermodError('Cannot find ONE simple answer')
        else:
            pass
        c.close()

if __name__=="__main__":
    db = MySQLdb.connect(host=config.get('WRITE_SQL','host'), user=config.get('WRITE_SQL','user'), passwd=config.get('WRITE_SQL','passwd'), db='smr')
    x = Level2(0x772B,1,6,29,'2-1',db)
    x.setFileNames()
    x.readAuxFile()
    x.readData()
    x.addData()
    x.upload()
