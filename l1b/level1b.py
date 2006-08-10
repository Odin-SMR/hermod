#!/usr/bin/python

import MySQLdb
import sys
import shutil
import os
import re
import glob,commands,ReadHDF,transitions
from hermod import hermodBase

class Level1b:
    def __init__(self,file,openDatabase):
        self.origHDFfile = file
        self.origLOGfile = os.path.splitext(file)[0] + ".LOG"
        self.openDB = openDatabase
        self.readL1b()
        self.setNames()
        self.getScans()

    def readL1b(self):
        name,extension, = os.path.splitext(self.origHDFfile)
        if extension==".HDF":
            lists = ReadHDF.read(self.origHDFfile)
            keys = ["Version","Level","MJD","Orbit","Source","Type","Latitude","Longitude","SunZD"]
            self.SMR = [ dict(zip(keys,d)) for d in lists ]
        else:
            mesg = "%s: Not a valid extension: %s \n" % (file,extension)
            raise HermodError(mesg)

    def setNames(self):
        #Reads sourcesfield and gives a list of freqmodes in the file
        self.freqmodes = list(set([int(y['Source'].split('FM=')[1]) for y in self.SMR]))
        self.freqmodes.append(0)
        calibrations = list(set([y['Level']&0xff for y in self.SMR]))
        orbits = list(set([int(y['Orbit']) for y in self.SMR]))
        if len(calibrations)<>1:
            raise HermodError("-None or many calibrations")
        if len(orbits)<>1:
            raise HermodError("-None or many orbits")
        self.calibration = calibrations[0]
        self.orbit = orbits[0]
        cur = self.openDB.cursor(MySQLdb.cursors.DictCursor)
        status = cur.execute("""select distinct backend,prefix from Freqmodes where freqmode in %s""",(self.freqmodes,))
        for i in cur: # This is only supposed to run once
            self.destHDFfile = "%s/V-%i/%s/%0.2X/%s%0.4X.HDF" %(LEVEL1B_DIR,self.calibration,i['backend'],self.orbit>>8,i['prefix'],self.orbit)
            self.destLOGfile = "%s/V-%i/%s/%0.2X/%s%0.4X.LOG" %(LEVEL1B_DIR,self.calibration,i['backend'],self.orbit>>8,i['prefix'],self.orbit)
            self.destZPTfile = "%s/V-%i/%s/%0.2X/%s%0.4X.ZPT" %(LEVEL1B_DIR,self.calibration,i['backend'],self.orbit>>8,i['prefix'],self.orbit)
            self.linkZPTfile = "%s/V-%i/ECMWF/%s/%s%0.4X.ZPT" %(SMRL1B_DIR,self.calibration,i['backend'],i['prefix'],self.orbit)
        status = cur.execute("""select * from Freqmodes where freqmode in %s""",(self.freqmodes,))
        self.transitions= [transitions.Transition(a,self) for a in cur]
        cur.close()
        
    def getScans(self):
        scan=[]
        reset = False
        for i,v in enumerate([y['Type'] for y in self.SMR]):
            if v==8:
                if reset:
                    scan.append(i)
                    reset=False
                else:
                    pass
            elif v==3:
                reset=True
        self.scans = [ self.SMR[i] for i in scan]

    def cleanDatabase(self):
        cur = self.openDB.cursor()
        # Removing all scans from level2, level1b and scans tables from this new file
        for freqmode in self.freqmodes:
            l2status = cur.execute("""  delete level2
                                from scans, level2
                                where scans.id=level2.id 
                                    and orbit=%s 
                                    and freqmode = %s 
                                    and calibration=%s """,(self.orbit,freqmode,self.calibration))

            l1bstatus = cur.execute("""  delete level1b
                                from scans ,level1b
                                where scans.id=level1b.id 
                                    and orbit=%s
                                    and freqmode = %s
                                    and calibration=%s """,(self.orbit,freqmode,self.calibration))

            scanstatus = cur.execute("""  delete from scans
                                where orbit=%s
                                    and freqmode = %s
                                    and calibration=%s """,(self.orbit,freqmode,self.calibration))
        cur.close()
        return (l2status,l1bstatus,scanstatus)

    def addDataL1b(self):
        # Adding data from file
        c = self.openDB.cursor()
        scan_values = [(int(v['Orbit']),int(v['Source'].split('FM=')[1]),v['Level']&0xff,i+1) for i,v in enumerate(self.scans)]
        scan_status = c.executemany(""" insert scans 
                            (orbit,freqmode,calibration,scan) 
                            values (%s,%s,%s,%s) """,scan_values)
        level1b_values = [(v['Version']>>8,v['Version']&0xFF,v['Level']>>8,v['MJD'],mjdtoutc(v['MJD']),v['Latitude'],v['Longitude'],int(v['Orbit']),int(v['Source'].split('FM=')[1]),v['Level']&0xff,i+1) for i,v in enumerate(self.scans)]
        for level1b_value in level1b_values:
            c.execute(""" insert level1b
                            (id,formatMajor,formatMinor,attitudeVersion,mjd,date,latitude,longitude,rssdate)
                            select id,%s,%s,%s,%s,%s,%s,%s,now()
                            from scans
                            where scans.orbit=%s and scans.freqmode=%s and scans.calibration=%s 
                                and scans.scan=%s """,level1b_value)
        c.close()

    def moveCreateFiles(self,qos):
        for i in [self.destHDFfile,self.destLOGfile,self.destZPTfile]:
            directory = os.path.basename(i)
            if os.path.exists(directory):
                pass
            else:
                try:
                    os.makedirs(directory)
                except IOError,inst:
                    mesg = """Errormessage: "%s" 
    ...while makeing directory %s\n""" % (str(inst),directory)
                    sys.stderr.write(mesg)
                    sys.excepthook(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
                
        try:
            shutil.move(self.origHDFfile,self.destHDFfile)
        except IOError,inst:
            mesg = """Errormessage: "%s"
    ...while moving %s 
        to %s\n""" % (str(inst),self.origHDFfile,self.destHDFfile)
            sys.stderr.write(mesg)
            sys.excepthook(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
        try:
            shutil.move(self.origLOGfile,self.destLOGfile)
        except IOError,inst:
            mesg = """Errormessage: "%s" 
    ...while moving %s 
        to %s\n""" % (str(inst),self.origLOGfile,self.destLOGfile)
            sys.stderr.write(mesg)
            sys.excepthook(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
        self.createZPT()
        for a in self.transitions:
            a.createDirectories()
            a.createLink()
            a.queue(qos)
 
    def createZPT():
        f,h,g = os.popen3("/home/odinop/bin/create_tp_ecmwf_rss2 " + self.destLOGfile)
        f.close()
        h.close()
        lines = g.readlines()
        g.close()
        if lines<>[]:
            sys.stderr.writelines()
        try:
            os.remove(self.linkZPTfile)
        except OSError:
            pass
        try:
            os.symlink(self.destZPTfile,self.linkZPTfile)
        except OSError,inst:
            mesg = """Errormessage: "%s" 
    ...while symlinking %s 
        to %s\n""" % (str(inst),self.destZPTfile,self.linkZPTfile)
            sys.stderr.write(mesg)
            sys.excepthook(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])


           
def test(file):
    db = MySQLdb.connect(host="jet",user="odinuser",passwd="***REMOVED***",db="odin")
    x = Level1b(file,db)
    x.transitions[0].queue()
    db.close()
    return x
