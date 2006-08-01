#!/usr/bin/python

import MySQLdb
import sys
import shutil
import os
import re
import glob,commands

#Set path
SPOOL_DIR= "/odin/smr/Data/spool/"
FAILURE_DIR="/odin/smr/Data/spool_failure/"
MISSING_LOG="/odin/smr/Data/spool_missing/"
LEVEL1B_DIR= "/odin/smr/Data/level1b/"
SMRL1B_DIR="/odin/smr/Data/SMRl1b/"

#Connect to database
db=MySQLdb.connect(host="jet",user="odinuser",passwd="***REMOVED***",db="odin")

def main():
    files=sys.argv[1:]
    #for every file in argumentlist
    for file in files:
        name,extention,=os.path.splitext(file)
        if not extention==".HDF":
            mesg = "%s: Not a valid extention: %s \n" % (file,extention)
            sys.stderr.write(mesg)
            continue
        basename = os.path.basename(file)
        data=readFile(file)
        scans=getScans(data)
        if len(scans)<3:
            #move file to /odin/smr/Data/spool_failure
	    try:
                shutil.move(name+".LOG",FAILURE_DIR)
	    except:
                text ="hermod: error couldn't move : %s.LOG to failure directory\n" % (name)
                sys.stderr.write(text)
                shutil.move(file,MISSING_LOG)
            try:
		shutil.move(file,FAILURE_DIR)
	    except:
                text ="hermod: error couldn't move : %s to failure directory\n" % (file)
                sys.stderr.write(text)
	    continue
        fqnr,cal,orbit, = fileInfo(scans)

        #destination
        backends = ["AC0","AC1","AC2"]
        indexlist = ["A","B","C"]
        backend = backends[indexlist.index(basename[1])]
        
        l1bdir = "%sV-%d/%s/%0.2X/" %(LEVEL1B_DIR,cal,backend,orbit>>8)
        if not os.path.exists(l1bdir):
            os.makedirs(l1bdir,0755)
        try:
            shutil.move(name+".LOG",l1bdir)
        except: 
            #if no logfile don't leave this file in spooldir
            shutil.move(file,MISSING_LOG)
            text="no logfile for file %s\n" % (file)
            sys.stderr.write(text)
            continue
        
        shutil.move(file,l1bdir)
        
        c=db.cursor()
        #fake fqmode to make Mysqld get it right, I add a none existing freqmode to make fm a list...
        fqnr.append(223)
        # Find all modenames assigned to the fqnr-list
        status = c.execute("""  select name
                                from Freqmodes
                                where freqmode in %s""",(fqnr,))
        modes = c.fetchall()

        # loop over all available modes and link files to SMR-tree
        for m in modes:
            modename = m[0]
            symdest = "%sV-%d/%s/" %(SMRL1B_DIR,cal,modename)
            if not os.path.exists(symdest):
                os.makedirs(symdest,0755)

            dstl = symdest + os.path.basename(name) + ".LOG"
            srcl = l1bdir  + os.path.basename(name) + ".LOG"
            if os.path.exists(dstl):
                os.remove(dstl)
            try:
                os.symlink(srcl,dstl)
            except:
                msg = "Could not link logfile %s to %s\n" % (srcl,dstl)
                sys.err.write(msg)
                sys.exit(1)
                
            dsth = symdest + os.path.basename(name) + ".HDF"
            srch = l1bdir  + os.path.basename(name) + ".HDF"
            if os.path.exists(dsth):
                os.remove(dsth)
            try:
                os.symlink(srch,dsth)
            except:
                msg = "Could not link hdf file %s to %s\n" % (srch,dsth)
                sys.err.write(msg)
                sys.exit(1)
                 

        #create zpt-files
        zptcom = "~/bin/create_tp_ecmwf_rss2 %s%s.LOG" %(l1bdir,os.path.basename(name))
        os.system(zptcom)
        symdest = "%sV-%d/ECMWF/%s/" %(SMRL1B_DIR,cal,backend[0][0])
        if not os.path.exists(symdest):
           os.makedirs(symdest,0755)

        dstz = symdest + os.path.basename(name) + ".ZPT"
        srcz = l1bdir    + os.path.basename(name) + ".ZPT"
        if os.path.islink(dstz):
            os.remove(dstz)
        try:
            os.symlink(srcz,dstz)
        except:
           msg = "Could not link logfile %s to %s\n" % (srcl,dstl)
           sys.err.write(msg)
           sys.exit(1)

        
        # Removing all scans from level2, level1b and scans tables from this new file
        status = c.execute("""  delete level2
                                from scans, level2
                                where scans.id=level2.id 
                                    and orbit=%s 
                                    and freqmode in %s 
                                    and calibration=%s """,(orbit,fqnr,cal))
        print "scans removed from level2: " + str(status)

        status = c.execute("""  delete level1b
                                from scans ,level1b
                                where scans.id=level1b.id 
                                    and orbit=%s
                                    and freqmode in %s
                                    and calibration=%s """,(orbit,fqnr,cal))
        print "scan removed from level1b: " + str(status)

        status = c.execute("""  delete from scans
                                where orbit=%s
                                    and freqmode in %s
                                    and calibration=%s """,(orbit,fqnr,cal))
        print "scans removed from scans: " + str(status)
        
        
        # Adding data from file
        for i in scans:
            c.execute(""" insert scans 
                            (orbit,freqmode,calibration,scan) 
                            values (%s,%s,%s,%s) """,(i['Orbit'],i['fm'],i['cal'],i['nr']))
            c.execute(""" insert level1b
                            (id,formatMajor,formatMinor,attitudeVersion,mjd,date,latitude,longitude,rssdate)
                            select id,%s,%s,%s,%s,%s,%s,%s,now()
                            from scans
                            where scans.orbit=%s and scans.freqmode=%s and scans.calibration=%s 
                                and scans.scan=%s """,(i['Version']>>8,i['Version']&0xFF,i['Level']>>8,i['MJD'],mjdtoutc(i['MJD']),i['Latitude'],i['Longitude'],i['Orbit'],i['fm'],i['cal'],i['nr']))

        
        
        # Starting jobs related to the file
        status = c.execute("""  select maxproctime,Freqmodes.freqmode,name,Freqmodes.fqid,qsmr 
                                from Freqmodes natural join Versions
                                where Freqmodes.freqmode in %s and calibration=%s and active""",(fqnr,cal))

        active_modes = c.fetchall()
        #for every active freqmode queue a job
        for amode in active_modes:
            process_time = amode[0]
            fmnr = amode[1]
            fmname = amode[2]
            fqid = amode[3]
            version = amode[4]

            com = "cd /home/odinop/logs && echo \"~/bin/odinrun_Qsmr-%s %X %d %s\" | qsub -qstratos -l walltime=%s -N %s.%X.%s\n" % (version,orbit,cal,fmname,process_time,fmname,orbit,version)
            stin,stou,sterr = os.popen3(com)
            sout = stou.readlines()
            serr = sterr.readlines()
            print sout
            print serr
            sterr.close()
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
                       from scans natural join level2
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
                        (id,formatMajor,formatMinor,attitudeVersion,mjd,date,latitude,longitude,rssdate)
                        select id,%s,%s,%s,%s,%s,%s,%s,now()
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
        if len(fmnr)==2:
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
                if len(fmnr)==2:
                    i['fm']=int(fmnr[1])
                else:
                    i['fm']=0
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
    dir = "%sV-%d/%s/%0.2X/" %(LEVEL1B_DIR,cal,result[0][0],orb>>8)
    cc.close()
    return dir

def genSMRL1bDir(fmname,cal):
    dir = "%sV-%d/%s/" %(SMRL1B_DIR,cal,fmname)
    return dir

if __name__ == "__main__":
    main()
