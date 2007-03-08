#!/usr/bin/python

"""
This module aims to give a complet solution to the level1b koncept.
"""

import MySQLdb
import sys
import shutil
import os
from hermod.hermodBase import *
from hermod.l1b import ReadHDF
from hermod.l1b import transitions

class Level1b:
    """
    Main class, sets values read from the HDFfile.
    """

    def __init__(self,file,openDatabase):
        """
        Initiates an instance from a HDFfile
        """
        self.origHDFfile = file
        self.origLOGfile = os.path.splitext(file)[0] + ".LOG"
        self.openDB = openDatabase
        self.readL1b()
        self.setNames()
        self.getScans()

    def readL1b(self):
        """
        Reads HDF data from the ReadHDF module (external module written in C)
        """
        name,extension, = os.path.splitext(self.origHDFfile)
        if extension==".HDF":
            lists = ReadHDF.read(self.origHDFfile)
            keys = ["Version","Level","MJD","Orbit","Source","Type","Latitude","Longitude","SunZD"]
            self.SMR = [ dict(zip(keys,d)) for d in lists ]
        else:
            mesg = "%s: Not a valid extension: %s \n" % (self.origHDFfile,extension)
            raise HermodError(mesg)

    def setNames(self):
        """
        Set all variables based on HDFfile information
        """
        #Reads sourcesfield and gives a list of freqmodes in the file
        freqmodes = [0]
        for y in self.SMR:
            parts = y["Source"].split("FM=")
            if len(parts)>1:
                freqmodes.append(int(parts[1]))
        self.freqmodes = list(set(freqmodes))
        if len(self.freqmodes)<2:
            mesg = "%s: Error: No freqmode information in 'source' string" % self.origHDFfile
            raise HermodError(mesg)
        #Extract calibration from Level field
        calibrations = list(set([y['Level']&0xff for y in self.SMR]))
        if len(calibrations)<>1:
            self.calibration = calibrations[1]
        else:
            self.calibration = calibrations[0]

        #orbits
        orbits = list(set([int(y['Orbit']) for y in self.SMR]))
        if len(orbits)<>1:
            mesg = '%s: Error: File contain spectra from more than one orbit %s' %(self.origHDFfile,str(orbits))
            raise HermodError(mesg)
        self.orbit = orbits[0]

        #set name on related files
        cur = self.openDB.cursor(MySQLdb.cursors.DictCursor)
        status = cur.execute("""select distinct backend,prefix from Freqmodes where freqmode in %s""",(self.freqmodes,))
        for i in cur: # This is only supposed to run once
            self.destHDFfile = "%sV-%i/%s/%0.2X/%s%0.4X.HDF" %(LEVEL1B_DIR,self.calibration,i['backend'],self.orbit>>8,i['prefix'],self.orbit)
            self.destLOGfile = "%sV-%i/%s/%0.2X/%s%0.4X.LOG" %(LEVEL1B_DIR,self.calibration,i['backend'],self.orbit>>8,i['prefix'],self.orbit)
            self.destZPTfile = "%sV-%i/%s/%0.2X/%s%0.4X.ZPT" %(LEVEL1B_DIR,self.calibration,i['backend'],self.orbit>>8,i['prefix'],self.orbit)
            self.linkZPTfile = "%sV-%i/ECMWF/%s/%s%0.4X.ZPT" %(SMRL1B_DIR,self.calibration,i['backend'],i['prefix'],self.orbit)
        status = cur.execute("""select * from Freqmodes where freqmode in %s""",(self.freqmodes,))
        self.transitions= [transitions.Transition(a,self) for a in cur]
        cur.close()
        
    def getScans(self):
        """
        Divide spectra into scans
        """
        scan=[]
        reset = False
        for i,v in enumerate([y['Type'] for y in self.SMR]):
            if v==8:
                ### signal spectrum
                if reset:
                    scan.append(i)
                    reset=False
                else:
                    pass
            elif v==3:
                ### calibration spectrum
                reset=True
        self.scans = [ self.SMR[i] for i in scan]

    def cleanDatabase(self):
        """
        Removes all occurrancies of this orbitfile in database
        """
        if not config.getboolean('DEFAULT','debug'):
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
        else:
            pass
            # do nothing
        return (l2status,l1bstatus,scanstatus)

    def addDataL1b(self):
        """
        Add data to database
        """
        if not config.getboolean('DEFAULT','debug'):
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
        else:
            pass
            # Do nothing debug is active

    def moveCreateFiles(self,queue):
        """
        Move files to its final position, create links and send to queue
        """
        if not config.getboolean('DEFAULT','debug'):
            for i in [self.destHDFfile,self.destLOGfile,self.destZPTfile]:
                directory = os.path.dirname(i)
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
                a.queue(queue)
        else:
            pass
            #Do nothing debug is active
 
    def createZPT(self):
        """
        Creates ZPT file
        """
        if not config.getboolean('DEFAULT','debug'):
            f,h,g = os.popen3("/home/odinop/bin/create_tp_ecmwf_rss2 " + self.destLOGfile)
            f.close()
            h.close()
            lines = g.readlines()
            g.close()
            if lines<>[]:
                sys.stderr.writelines(lines)
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
        else:
            pass
            #Do nothing debug is active

class Level1bResolver(Level1b):
    def __init__(self,orbitDecNr,calibration,freqmode,fqid,vers,openDatabase):
        self.freqmodes = [freqmode]
        self.orbit = orbitDecNr
        self.calibration = calibration
        self.fqid = fqid
        self.qsmr = vers
        self.openDB = openDatabase
        self.origHDFfile = ""
        self.origLOGfile = ""
        self.setNames()

    def setNames(self):
        cur = self.openDB.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("""select * from Freqmodes where freqmode=%s and fqid=%s""",(self.freqmodes[0],self.fqid))
        for i in cur: # This is only supposed to run once
            self.destHDFfile = "%sV-%i/%s/%0.2X/%s%0.4X.HDF" %(LEVEL1B_DIR,self.calibration,i['backend'],self.orbit>>8,i['prefix'],self.orbit)
            self.destLOGfile = "%sV-%i/%s/%0.2X/%s%0.4X.LOG" %(LEVEL1B_DIR,self.calibration,i['backend'],self.orbit>>8,i['prefix'],self.orbit)
            self.destZPTfile = "%sV-%i/%s/%0.2X/%s%0.4X.ZPT" %(LEVEL1B_DIR,self.calibration,i['backend'],self.orbit>>8,i['prefix'],self.orbit)
            self.linkZPTfile = "%sV-%i/ECMWF/%s/%s%0.4X.ZPT" %(SMRL1B_DIR,self.calibration,i['backend'],i['prefix'],self.orbit)
        self.transitions= [transitions.Transition(a,self) for a in cur]
        cur.close()
    
    def cleanDatabase(self):
        if not config.getboolean('DEFAULT','debug'):
            cur = self.openDB.cursor()
            # Removing all scans from level2, level1b and scans tables from this new file
            for freqmode in self.freqmodes:
                l2status = cur.execute("""  delete level2
                                    from scans, level2
                                    where scans.id=level2.id 
                                        and orbit=%s 
                                        and freqmode = %s 
                                        and calibration=%s """,(self.orbit,freqmode,self.calibration))
    
            cur.close()
            return l2status
        else:
            pass
            #Do nothing debug is active

    def createFiles(self,queue,qsmr):
        if not config.getboolean('DEFAULT','debug'):
            self.createZPT()
            for a in self.transitions:
                a.forceQueue(queue,qsmr)
        else:
            pass
            # Do nothing debug is active
 
           
def test(file):
    db = MySQLdb.connect(host=config.get('WRITE_SQL','host'), user=config.get('WRITE_SQL','user'), passwd=config.get('WRITE_SQL','passwd'), db=config.get('WRITE_SQL','db'))
    x = Level1b(file,db)
    x.transitions[0].queue()
    db.close()
    return x
