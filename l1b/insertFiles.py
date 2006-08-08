#!/usr/bin/python

import MySQLdb
import sys
import shutil
import os
import re
import glob,commands,ReadHDF,transitions

#Set path
SPOOL_DIR= "/odin/smr/Data/spool"
FAILURE_DIR="/odin/smr/Data/spool_failure"
MISSING_LOG="/odin/smr/Data/spool_missing"
LEVEL1B_DIR= "/odin/smr/Data/level1b"
SMRL1B_DIR="/odin/smr/Data/SMRl1b"

#Connect to database

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
            sys.stderr.write(mesg)
            sys.exit(1)

    def setNames(self):
        #Reads sourcesfield and gives a list of freqmodes in the file
        self.freqmodes = list(set([int(y['Source'].split('FM=')[1]) for y in self.SMR]))
        calibrations = list(set([y['Level']&0xff for y in self.SMR]))
        orbits = list(set([int(y['Orbit']) for y in self.SMR]))
        if len(calibrations)<>1:
            sys.stderr.write("Warning none or many calibrations")
            sys.exit(1)
        if len(orbits)<>1:
            sys.stderr.write("Warning none or many orbits")
            sys.exit(1)
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

    def moveCreateFiles(self):
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
        os.system("/home/odinop/bin/create_tp_ecmwf_rss2 " + self.destLOGfile)
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
        for a in self.transitions:
            a.createDirectories()
            a.moveCreateAndLink()
            a.queue()
            
def test(file):
    db = MySQLdb.connect(host="jet",user="odinuser",passwd="***REMOVED***",db="odin")
    x = Level1b(file,db)
    x.transitions[0].queue()
    db.close()
    return x

def main():
    db = MySQLdb.connect(host="jet",user="odinuser",passwd="***REMOVED***",db="odin")
    files=sys.argv[1:]
    #for every file in argumentlist
    for file in files:
        x = Level1b(file,db)
        x.cleanDatabase()
        x.addDataL1b()
        x.moveCreateFiles
    db.close()
        

def mjdtoutc(mjdnr):
    # Julian date
    jd = int(mjdnr) + 2400000.5

    # get the fraction of UTC day.
    dayfrac = mjdnr - int(mjdnr)

    # add a half
    jd0 = jd + .5

    # determin the calender
    if (jd0 < 2299161.0):
        # Julian 
        c = jd0 + 1524.0
    else:
        # Gregorian 
        b = int(((jd0 -1868216.25)/36524.25))
        c = jd0 + (b- int(b/4) + 1525.0)

    d     = int( ((c - 122.1) / 365.25) )
    e     = 365.0 * d + int(d/4)
    f     = int( ((c - e) / 30.6001) )
    day   = int( (c - e + 0.5) - int(30.6001 * f) )
    month = int( (f - 1 - 12*int(f/14)) );
    year  = int( ( d - 4715 - int((7+month)/10)) )
    hour     = int(dayfrac*24.0)
    minute      = int((dayfrac*1440.0)-int(dayfrac*1440.0/60)*60.0)
    dayfrac  = dayfrac * 86400.0
    ticks    = (dayfrac-int(dayfrac/60)*60.0)
    secs     = int(ticks)
    ticks    = ticks- secs
    ret = str(year)+"-"+str(month)+"-"+str(day)+" "+str(hour)+":"+str(minute)+":"+str(secs+ticks)
    return ret

    
#def readFile(file):
#    cur.close()
#    lists=ReadHDF.read(file)
#    all=[]
#    for list in lists:
#        value ={'Version':list[0],'Level':list[1],'MJD':list[2],'Orbit':int(list[3]),'Source':list[4],'Type':list[5],'Latitude':list[6],'Longitude':list[7],'SunZD':list[8]}
#        all.append(value)
#    return all

if __name__ == "__main__":
    main()
