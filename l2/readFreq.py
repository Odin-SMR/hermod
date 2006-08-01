#!/usr/bin/python

"""
This script is called after processing of a l2p-file in ~/bin/odinrun.
This script adds information to the database"

readFreq orbit calibration freqmode qsmrver

example:
    ./readFreq 5C52 4 SM_AC2ab 2-0
"""

import MySQLdb
import sys
import shutil
import os
import re
import glob

from pyhdf.HDF import *
from pyhdf.VS import *

MAX_NUMBER_OF_TRIES = 0
#Set path
l2dir = "/odin/smr/Data/SMRl2/"

#get commandline parameters
orbit=sys.argv[1]
cal=sys.argv[2]
freq=sys.argv[3]
qsmr=sys.argv[4]

print orbit
print cal
print freq
print

#Connect to database
db=MySQLdb.connect(host="jet",user="odinuser",passwd="***REMOVED***",db="odin")
c=db.cursor()

#find parameters in the database (Freqmodes,Versions)
status=c.execute("""select midfreq,l2prefix,l2p,qsmr,Freqmodes.freqmode,prefix,Freqmodes.fqid from Freqmodes natural join Versions where name=%s and calibration=%s and qsmr=%s""" ,(freq,cal,qsmr))
r=c.fetchall()
if status==0:
    mesg = sys.argv[0] + ": error resolving freqmode and calibration\n"
    sys.exit(mesg)

    
for modes in r:
    midfreq = modes[0]
    l2p = modes[1]
    qsmr = modes[2]
    freqmode = modes[4]
    prefix = modes[5]
    fqid = modes[6]
    hdffile = "%sSMRhdf/Qsmr-%s/%s/SCH_%s_%s%s_%s.L2P" %(l2dir,modes[3],freq,midfreq,modes[1],str(orbit).zfill(4),str(modes[2]).zfill(3))
    auxfile = "%sSMRhdf/Qsmr-%s/%s/SCH_%s_%s%s_%s.AUX" %(l2dir,modes[3],freq,modes[0],modes[1],str(orbit).zfill(4),str(modes[2]).zfill(3))
    inffile = "%sSMRhdf/Qsmr-%s/%s/SCH_%s_%s%s_%s.ERR" %(l2dir,modes[3],freq,modes[0],modes[1],str(orbit).zfill(4),str(modes[2]).zfill(3))
    matfile = "%sSMRmat/Qsmr-%s/%s/%s%s.mat" %(l2dir,modes[3],freq,modes[5],str(orbit).zfill(4))
    errfile = "%sSMRmat/Qsmr-%s/%s/%s%s.qsmr_error" %(l2dir,modes[3],freq,modes[5],str(orbit).zfill(4))
    efile   = "/home/odinop/logs/%s.%s.%s.e" %(freq,str(orbit).zfill(4),modes[3])
    ofile   = "/home/odinop/logs/%s.%s.%s.o" %(freq,str(orbit).zfill(4),modes[3])

    #clean up database: delete all records from this orbit,freqmod and version
    c.execute("""DELETE level2 FROM level2,scans WHERE orbit=%s and calibration=%s and freqmode=%s and version=%s and scans.id=level2.id and fqid=%s""",(int(orbit,16),cal,modes[4],modes[3],fqid))

    #add record in "Processed"
    test = c.execute("""select prnr from Processed where orbit=%s and freqmode=%s and version=%s""",(int(orbit,16),freq,modes[3]))
    if test==0:
        c.execute("""insert into Processed (orbit,freqmode,version,prdate) values (%s,%s,%s,now())""",(int(orbit,16),freq,modes[3]))
    else:
        c.execute("""update Processed set prnr=prnr+1,prdate=now() where orbit=%s and freqmode=%s and version=%s""",(int(orbit,16),freq,modes[3]))

    #remove old stderr/stdout files

    efiles = glob.glob(efile+"*")
    for i in efiles:
        os.system("rm -f " + i)

    ofiles = glob.glob(ofile+"*")
    for i in ofiles:
        os.system("rm -f " + i)

 
    #Read the hdffile
    try:
        f = HDF(hdffile)                # open 'inventory.hdf' in read mode
        vs = f.vstart()                 # init vdata interface
        vd = vs.attach('Geolocation')   # attach 'INVENTORY' in read mode
    except HDF4Error:
        test = c.execute("""select prnr from Processed where orbit=%s and freqmode=%s and version=%s""",(int(orbit,16),freq,modes[3]))
        num = c.fetchone()
        if num[0]>MAX_NUMBER_OF_TRIES:
            mesg = sys.argv[0] + ": error can't open file - " + hdffile + "\nNot rerunning qsmr - STOP"
        else:
            mesg = sys.argv[0] + ": error can't open file - " + hdffile + "\nRerunning qsmr"
            launchcmd = "~/bin/odinlaunch start %s %s %s %s" % (orbit,orbit,freq,modes[3])
            #    print launchcmd
            os.system(launchcmd)
        sys.exit(mesg)
    
    # Loop over the vdata records, displaying each record as a table row.
    # Current record position is 0 after attaching the vdata.
    while 1:
        try:
            rec = vd.read()         # read next record
        except HDF4Error:           # end of vdata reached
            break
        
        #nr,recordname
        #0 'Version1b'
        #1 'Version2'
        #2 'Quality'
        #3 'Source'
        #4 'ZPTSource'
        #5 'OrbitFilename'
        #6 'SunZD'
        #7 'LST'
        #8 'ScanNo'
        #9 'Nspecies'
        #10 'Day'
        #11 'Month'
        #12 'Year'
        #13 'Hour'
        #14 'Min'
        #15 'Secs'
        #16 'Ticks'
        #17 'Latitude'
        #18 'Longitude'
        #19 'StartLat'
        #20 'EndLat'
        #21 'StartLong'
        #22 'EndLong'
        #23 'StartTan'
        #24 'EndTan'
        #25 'MJD'
        #26 'Time'
        #27 'ID1'
        
        records = tuple(rec[0])
        #Add records to database
        for j in rec:
            date = "%s-%s-%s %s:%s:%s" %(records[12],records[11],records[10],records[13],records[14],records[15])
            test = c.execute("""    INSERT delayed INTO level2
                                    (processed,version,id,latitude,longitude,mjd,date,sunZD,poffset,fqid)
                                    SELECT now(),%s,scans.id,%s,%s,%s,%s,%s,null,%s
                                    FROM scans
                                    WHERE scans.freqmode=%s 
                                        and scans.orbit=%s 
                                        and scans.calibration=%s 
                                        and scans.scan=%s """, (modes[3],records[17],records[18],records[25],date,records[6],fqid,modes[4],int(orbit,16),cal,records[8]))
    
    vd.detach()               # "close" the vdata
    vs.end()                  # terminate the vdata interface
    f.close()                 # close the HDF file
    
    
    ##Read the matfiles
    #stdin,stdout, = os.popen4("~/hermod/mat/poff.sh " + matfile)
    #rawtext = stdout.read()
    #stdin.close()
    #stdout.close()
    #pat1=re.compile("!!,(.*),.*")
    #pat2=re.compile("!!,.*,(.*)")
    #scan = map(int,pat1.findall(rawtext))
    #poff = map(float,pat2.findall(rawtext))
    #poffpair=zip(scan,poff)
    #for i in poffpair:
    #    test = c.execute("""
    #update low_priority level2,scans set poffset=%s where calibration=%s and scan=%s and hex(orbit)=%s and freqmode=%s and level2.id=scans.id and version=%s;
    #""",(i[1],cal,i[0],orbit,modes[4],modes[3]))
    #    if glob.glob(errfile)!=[]:
    #        shutil.move(errfile,inffile)
    os.system("rm -f "+matfile)
    #
    #
