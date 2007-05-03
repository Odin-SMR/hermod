import MySQLdb
import sys
import shutil
import os
import re

from pyhdf.HDF import *
from pyhdf.VS import *
from hermod.hermodBase import *

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

    def setFileNames(self):
        """
        Looks up parameters in odin database and creates all the filenames that concerns SMR information
        """
        c=self.db.cursor(MySQLdb.cursors.DictCursor)
        #find parameters in the database (Freqmodes,Versions)
        status=c.execute ("""select * from Freqmodes natural join Versions where Freqmodes.freqmode=%s and calibration=%s and Freqmodes.fqid=%s and qsmr=%s""" ,(self.freqmode,self.calibration,self.fqid,self.version))
        if status==1:
            row = c.fetchone()
            self.hdffile = "%sSMRhdf/Qsmr-%s/%s/SCH_%s_%s%0.4X_%s.L2P" %(SMRL2_DIR,row['qsmr'],row['name'],row['midfreq'],row['l2prefix'],self.orbit,str(row['l2p']).zfill(3))
            self.auxfile = "%sSMRhdf/Qsmr-%s/%s/SCH_%s_%s%0.4X_%s.AUX" %(SMRL2_DIR,row['qsmr'],row['name'],row['midfreq'],row['l2prefix'],self.orbit,str(row['l2p']).zfill(3))
            self.inffile = "%sSMRhdf/Qsmr-%s/%s/SCH_%s_%s%0.4X_%s.ERR" %(SMRL2_DIR,row['qsmr'],row['name'],row['midfreq'],row['l2prefix'],self.orbit,str(row['l2p']).zfill(3))
            self.matfile = "%sSMRmat/Qsmr-%s/%s/%s%0.4X.mat" %(SMRL2_DIR,row['qsmr'],row['name'],row['prefix'],self.orbit)
            self.errfile = "%sSMRmat/Qsmr-%s/%s/%s%0.4X.qsmr_error" %(SMRL2_DIR,row['qsmr'],row['name'],row['prefix'],self.orbit)
            self.destHDFfile = "%sV-%i/%s/%0.2X/%s%0.4X.HDF" %(LEVEL1B_DIR,self.calibration,row['backend'],self.orbit>>8,row['prefix'],self.orbit)
            self.destLOGfile = "%sV-%i/%s/%0.2X/%s%0.4X.LOG" %(LEVEL1B_DIR,self.calibration,row['backend'],self.orbit>>8,row['prefix'],self.orbit)
            self.destZPTfile = "%sV-%i/%s/%0.2X/%s%0.4X.ZPT" %(LEVEL1B_DIR,self.calibration,row['backend'],self.orbit>>8,row['prefix'],self.orbit)
            self.linkZPTfile = "%sV-%i/ECMWF/%s/%s%0.4X.ZPT" %(SMRL1B_DIR,self.calibration,row['backend'],row['prefix'],self.orbit)
                                                        
        else:
            if status>1:
                mesg = "Two or more modes matches CRITICAL WARNING this is a design error"
                raise HermodError(mesg)
            mesg = "Error resolving freqmode and calibration"
            raise HermodError(mesg)
        c.close()
       
    def readl2(self):
        """
        Reads a the associated hdf file. Returns a list of dictionaries. If an error occurs it returns an empty list.
        """
        table = "Geolocation"
        try:
            f = HDF(self.hdffile)                # open 'inventory.hdf' in read mode
            vs = f.vstart()                 # init vdata interface
            vd = vs.attach(table)   # attach 'INVENTORY' in read mode
            index = vd.inquire()[2]
            self.geolocation = [ dict(zip(index,d)) for d in vd[:] ]
            vd.detach()               # "close" the vdata
            vs.end()                  # terminate the vdata interface
            f.close()                 # close the HDF file
        except HDF4Error:
            mesg = "error reading %s" % self.hdffile
            raise HermodError(mesg)

    def addData(self):
        """
        Adds data into the odin database
        """
        cleartoinsert = True
        neededkeys = ["SunZD","ScanNo","Day","Month","Year","Hour","Min","Secs","Latitude","Longitude","MJD"]
        c = self.db.cursor()
        for records in self.geolocation:
           date = "%s-%s-%s %s:%s:%s" %(records['Year'],records['Month'],records['Day'],records['Hour'],records['Min'],records['Secs'])
           test = c.execute("""    INSERT delayed INTO level2
                                   (processed,version,id,latitude,longitude,mjd,date,sunZD,poffset,fqid)
                                   SELECT now(),%s,scans.id,%s,%s,%s,%s,%s,null,%s
                                   FROM scans
                                   WHERE scans.freqmode=%s 
                                       and scans.orbit=%s 
                                       and scans.calibration=%s 
                                       and scans.scan=%s """, (self.version,records['Latitude'],records['Longitude'],records['MJD'],date,records['SunZD'],self.fqid,self.freqmode,self.orbit,self.calibration,records["ScanNo"]))
        c.close()
        return test
    
    def readAuxFile():
        data=[]
        typelist = [int,float,float,str,int,float,int,float,float,float,float,float,float,float,float,int]
        f = open(self.auxfile)
        try:
            head = f.readline()
            header = head.split()[1:]
            for line in f:
                    fields = line.split()
                    converted = [g(h) for g,h in zip(typelist,fields)]
                    data.append(dict(zip(header,converted))) 
        finally:
            f.close()
        self.aux = data

    def dell2(self):
        """
        Deletes an instance from the level2 table in the odin database
        """
        cursor = self.db.cursor()
        status = cursor.execute("""DELETE level2 FROM level2,scans WHERE orbit=%s and calibration=%s and freqmode=%s and version=%s and scans.id=level2.id and fqid=%s""",(self.orbit,self.calibration,self.freqmode,self.version,self.fqid))
        cursor.close()
        return status
         
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
