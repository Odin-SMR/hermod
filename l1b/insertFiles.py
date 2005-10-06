#!/usr/bin/python

import MySQLdb
import sys
import shutil
import os
import re
import glob,commands

#Set path
SPOOL_DIR= "/odin/smr/Data/spool/"
LEVEL1B_DIR= "/odin/smr/Data/level1b/"
SMRL1B_DIR="/odin/smr/Data/SMRl1b/"

#Connect to database
db=MySQLdb.connect(user="odinuser",passwd="***REMOVED***",db="odin")

def main():
    files=glob.glob(SPOOL_DIR+"*.HDF")
    #for every file
    for i in files:
        print i
        name,extention,=os.path.splitext(i)
        data=readFile(i)
        scans=getScans(data)
        if scans==[]:
            continue
        if len(scans)<3:
            continue
        fm,cal,orbit, = fileInfo(scans)
        print fm
        print cal
        print "%X" %(orbit)
        c=db.cursor()
        #fake fqmode to make Mysqld get it right
        fm.append(223)
        status = c.execute("""select name,maxproctime from Freqmodes where freqmode in %s and active""",(fm,))
        activefreq = c.fetchall()
        status = c.execute("""select name from Freqmodes where freqmode in %s""",(fm,))
        availfreq = c.fetchall()
        status = c.execute("""select distinct backend from Freqmodes where freqmode in %s""",(fm,))
        backend = c.fetchall()
        #copy file to position (version,freqmode needed)
        #delete spoolfile
        dest = genL1bDir(fm,cal,orbit)
        #remove fake fqmode
        fm.remove(223)
        if not os.path.exists(dest):
            os.makedirs(dest,0755)
        try:
            shutil.move(name+".LOG",dest)
        except: 
            #if no logfile leave this file in spooldir
            print "abort. no logfile"
            continue
        shutil.move(i,dest)
        for ii in availfreq:
            symdest = genSMRL1bDir(ii[0],cal)
            if not os.path.exists(symdest):
                os.makedirs(symdest,0755)

            dstl = symdest + os.path.basename(name) + ".LOG"
            srcl = dest    + os.path.basename(name) + ".LOG"
            if os.path.islink(dstl):
                os.remove(dstl)
            try:
                os.symlink(srcl,dstl)
            except:
                pass
            dsth = symdest + os.path.basename(name) + ".HDF"
            srch = dest    + os.path.basename(name) + ".HDF"
            if os.path.islink(dsth):
                os.remove(dsth)
            try:
                os.symlink(srch,dsth)
            except:
                pass
        #add scans to db
        addData(scans)

        #create zpt-files
        zptcom = "~/bin/createzpt.sh %s%s.LOG" %(dest,os.path.basename(name))
        stin,stou, = os.popen4(zptcom)
        lines=stou.readlines()
        stin.close()
        stou.close()
        symdest = "%sV-%d/ECMWF/%s/" %(SMRL1B_DIR,cal,backend[0][0])
        if not os.path.exists(symdest):
           os.makedirs(symdest,0755)

        dstz = symdest + os.path.basename(name) + ".ZPT"
        srcz = dest    + os.path.basename(name) + ".ZPT"
        if os.path.islink(dstz):
            os.remove(dstz)
        try:
            os.symlink(srcz,dstz)
        except:
           pass
        #for every active freqmode queue a job
        for ii in activefreq:
            com = "cd /home/odinop/logs && echo \"~/bin/odinrun_Qsmr-2-0 %X %d %s\" | qsub -qstratos -l walltime=%s -N %s.%X.2-0\n" % (orbit,cal,ii[0],ii[1],ii[0],orbit)
            print com
            stin,stou, = os.popen4(com)
            lines = stou.readlines()
            stin.close()
            stou.close()
            
            

def addData(sc):
    cur = db.cursor()
    a=[]
    for i in sc:
        param = (i['Orbit'],i['fm'],i['cal'])
        if not param in a:
            a.append(param)
    for ii in a:
        cur.execute("""delete level2
                        from scans,level2
                        where orbit=%s and freqmode=%s 
                            and calibration=%s
                            and scans.id=level2.id""",(ii[0],ii[1],ii[2]))
        
        cur.execute("""delete level1b
                        from scans,level1b
                        where orbit=%s and freqmode=%s 
                            and calibration=%s
                            and scans.id=level1b.id""",(ii[0],ii[1],ii[2]))
        cur.execute("""delete 
                        from scans
                        where orbit=%s and freqmode=%s 
                            and calibration=%s""",(ii[0],ii[1],ii[2]))
    for i in sc:
        cur.execute("""insert scans 
                        (orbit,freqmode,calibration,scan) 
                        values (%s,%s,%s,%s)""",(i['Orbit'],i['fm'],i['cal'],i['nr']))
        cur.execute("""insert level1b
                        (id,formatMajor,formatMinor,attitudeVersion,mjd,date,latitude,longitude)
                        select id,%s,%s,%s,%s,%s,%s,%s
                        from scans
                        where scans.orbit=%s and scans.freqmode=%s and scans.calibration=%s 
                            and scans.scan=%s""",(i['Version']>>8,i['Version']&0xFF,i['Level']>>8,i['MJD'],mjdtoutc(i['MJD']),i['Latitude'],i['Longitude'],i['Orbit'],i['fm'],i['cal'],i['nr']))
            

def fileInfo(scans):
    cal=scans[0]['Level']&0xFF
    fm = getFM(scans)
    orbit=scans[2]['Orbit']
    return (fm,cal,orbit)

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

    
def getFM(scan):
    fm = []
    for i in scan:
        fmnr=i['Source'].split("=")
        if not int(fmnr[1]) in fm:
            fm.append(int(fmnr[1]))
    return fm

def getScans(data):
    scan=[]
    spekt=0
    count=0
    reset = False
    for i in data:
        spekt=spekt+1
        if i['Type']==8:
            if reset:
                count=count+1
                fmnr=i['Source'].split("=")
                i['fm']=int(fmnr[1])
                i['cal']=i['Level']&0xFF
                i['att']=i['Level']>>8
                i['nr']=count
                scan.append(i)
                reset=False
            else:
                pass
        elif i['Type']==3:
            reset=True
    return scan

def readFile(file):
    stin,stou, = os.popen4("~/hermod/l1b/read_hdf "+file)
    lines = stou.readlines()
    stin.close()
    stou.close()
    all=[]
    for i in lines:
        list=i.split(";")
        value ={'Version':int(list[0]),'Level':int(list[1]),'MJD':float(list[2]),'Orbit':int(float(list[3])),'Source':list[4],'Type':int(list[5]),'Latitude':float(list[6]),'Longitude':float(list[7]),'SunSD':float(list[8])}
        all.append(value)
    return all

def genL1bDir(fmname,cal,orb):
    cc= db.cursor()
    status = cc.execute("""select distinct backend from Freqmodes where freqmode in %s""",(fmname,))
    result = cc.fetchall()
    dir = "%sV-%d/%s/%X/" %(LEVEL1B_DIR,cal,result[0][0],orb>>8)
    cc.close()
    return dir

def genSMRL1bDir(fmname,cal):
    dir = "%sV-%d/%s/" %(SMRL1B_DIR,cal,fmname)
    return dir

if __name__ == "__main__":
    main()
