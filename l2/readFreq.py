#!/usr/bin/python

""" 
This script is called after processing of a l2p-file in ~/bin/odinrun. It adds 
information to the database.

./readFreq.py <hex orbit> <calibration> <modename> <qsmr version>
  or preferably
./readFreq.py <orbit> <calibration> <freqmode> <fqid> <qsmr version>

The latter is prefered because is one sql-question faster and more secure for
future work. The first will be deprecated soon.

example:
    ./readFreq 5C52 4 SM_AC2ab 2-0
    ./readFreq 5C52 4 1 29 2-0
"""

import MySQLdb
import sys
import shutil
import os
import re

from pyhdf.HDF import *
from pyhdf.VS import *

#Set path
l2dir = "/odin/smr/Data/SMRl2/"

class Level2:
    
    def __init__(self,orbitNrDec,freqMode,calibration,fqid,version):
        """
        The constructor that should be used
        """
        self.orbit = orbitNrDec
        self.freqmode = freqMode
        self.calibration = calibration
        self.fqid = fqid
        self.version = version
        self.db = db=MySQLdb.connect(host="jet",user="odinuser",passwd="***REMOVED***",db="odin")
        self.setFileNames()

    def setFileNames(self):
        """
        Looks up parameters in odin database and creates all the filenames that concerns SMR information
        """
        c=self.db.cursor(MySQLdb.cursors.DictCursor)
        #find parameters in the database (Freqmodes,Versions)
        status=c.execute ("""select * from Freqmodes natural join Versions where Freqmodes.freqmode=%s and calibration=%s and Freqmodes.fqid=%s and qsmr=%s""" ,(self.freqmode,self.calibration,self.fqid,self.version))
        if status==1:
            row = c.fetchone()
            self.hdffile = "%sSMRhdf/Qsmr-%s/%s/SCH_%s_%s%0.4X_%s.L2P" %(l2dir,row['qsmr'],row['name'],row['midfreq'],row['l2prefix'],self.orbit,str(row['l2p']).zfill(3))
            self.auxfile = "%sSMRhdf/Qsmr-%s/%s/SCH_%s_%s%0.4X_%s.AUX" %(l2dir,row['qsmr'],row['name'],row['midfreq'],row['l2prefix'],self.orbit,str(row['l2p']).zfill(3))
            self.inffile = "%sSMRhdf/Qsmr-%s/%s/SCH_%s_%s%0.4X_%s.ERR" %(l2dir,row['qsmr'],row['name'],row['midfreq'],row['l2prefix'],self.orbit,str(row['l2p']).zfill(3))
            self.matfile = "%sSMRmat/Qsmr-%s/%s/%s%0.4X.mat" %(l2dir,row['qsmr'],row['name'],row['prefix'],self.orbit)
            self.errfile = "%sSMRmat/Qsmr-%s/%s/%s%0.4X.qsmr_error" %(l2dir,row['qsmr'],row['name'],row['prefix'],self.orbit)
        else:
            if status>1:
                mesg = sys.argv[0] + ": two or more modes matches CRITICAL WARNING this is a design error\n"
            mesg = sys.argv[0] + ": error resolving freqmode and calibration\n"
            sys.stderr.write(mesg)
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
            mesg = "error reading %s\n" % self.hdffile
            sys.stderr.write(mesg)

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
        shutil.move(self.errfile,self.inffile)

    def close(self):
        """
        Cleans object and closes open files and connections
        """
        self.db.close()

def usage():
    """
    Prints short manual
    """
    print """
This script is called after processing of a l2p-file in ~/bin/odinrun. It adds 
information to the database.

./readFreq.py <hex orbit> <calibration> <modename> <qsmr version>
  or preferably
./readFreq.py <orbit> <calibration> <freqmode> <fqid> <qsmr version>

The latter is prefered because it is one sql-question faster and more secure for
future work. The first will be deprecated soon.

example:
    ./readFreq 5C52 4 SM_AC2ab 2-0
    ./readFreq 5C52 4 1 29 2-0
    """

if __name__ == "__main__":
    #get commandline parameters

    if len(sys.argv) == 6:
        try:
            orbit=int(sys.argv[1],16)
            cal=int(sys.argv[2])
            freq=int(sys.argv[3])
            fqid=int(sys.argv[4])
            qsmr=sys.argv[5]
        except ValueError:
            usage()
            sys.exit(sys.argv[0] +": Not valid parmeters")
    else:
        if len(sys.argv) == 5:
            try:
                orbit=int(sys.argv[1],16)
                cal=int(sys.argv[2])
                mode=sys.argv[3]
                qsmr=sys.argv[4]
            except ValueError:
                usage()
                sys.exit(sys.argv[0] +": Not valid parmeters")
            db = MySQLdb.connect(host="jet",user="odinuser",passwd="***REMOVED***",db="odin")
            c = db.cursor()
            status=c.execute("""select Freqmodes.fqid ,Freqmodes.freqmode from Freqmodes natural join Versions where name=%s and calibration=%s and qsmr=%s""" ,(mode,cal,qsmr))
            r = c.fetchone()
            c.close()
            fqid = r[0]
            freq = r[1]
        else:
            if len(sys.argv) <> 6:
                usage()
                sys.exit(sys.argv[0] + ": Not correct number of parameters")
    l2p = Level2(orbit,freq,cal,fqid,qsmr)

    print """
    This is readfreq trying to add profiles to the database
    Now looking for orbit %0.4X mode %i in calibration %i 
    in version %s and fqid %i
    """ % (orbit,freq,cal,qsmr,fqid)

    l2p.dell2()
    l2p.readl2()
    l2p.addData()
    #l2p.cleanFiles()
    l2p.close()
    
#        ##Read the matfiles
#        #stdin,stdout, = os.popen4("~/hermod/mat/poff.sh " + matfile)
#        #rawtext = stdout.read()
#        #stdin.close()
#        #stdout.close()
#        #pat1=re.compile("!!,(.*),.*")
#        #pat2=re.compile("!!,.*,(.*)")
#        #scan = map(int,pat1.findall(rawtext))
#        #poff = map(float,pat2.findall(rawtext))
#        #poffpair=zip(scan,poff)
#        #for i in poffpair:
#        #    test = c.execute("""
#        #update low_priority level2,scans set poffset=%s where calibration=%s and scan=%s and hex(orbit)=%s and freqmode=%s and level2.id=scans.id and version=%s;
#        #""",(i[1],cal,i[0],orbit,modes[4],modes[3]))
#        #    if glob.glob(errfile)!=[]:
#        #
#        #
#        
