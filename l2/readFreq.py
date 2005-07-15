#!/usr/bin/python

"""
This script is called after processing of a l2p-file in ~/bin/odinrun.
This script adds information to the database"

readFreq orbit calibration freqmode

example:
    ./readFreq 5C52 4 SM_AC2ab
"""

import MySQLdb
import sys
import shutil
import os
import re
import glob

from pyhdf.HDF import *
from pyhdf.VS import *

MAX_NUMBER_OF_TRIES = 5
#Set path
l2dir = "/odin/smr/Data/SMRl2/"

#get commandline parameters
orbit=sys.argv[1]
cal=sys.argv[2]
freq=sys.argv[3]

#Connect to database
db=MySQLdb.connect(host="localhost",user="odinuser",passwd="***REMOVED***",db="odin")
c=db.cursor()

#find parameters in the database (Freqmodes,Currentversions)
cc=c.execute("""select midfreq,l2prefix,l2p,qsmr,freqmode,prefix from Freqmodes,Currentversions where name=%s and calibration=%s""" ,(freq,cal))
r=c.fetchone()
if cc!=1:
    mesg = sys.argv[0] + ": error resolving freqmode and calibration"
    sys.exit(mesg)
else:
    hdffile = "%sSMRhdf/Qsmr-%s/%s/SCH_%s_%s%s_%s.L2P" %(l2dir,r[3],freq,r[0],r[1],orbit,str(r[2]).zfill(3))
    auxfile = "%sSMRhdf/Qsmr-%s/%s/SCH_%s_%s%s_%s.AUX" %(l2dir,r[3],freq,r[0],r[1],orbit,str(r[2]).zfill(3))
    inffile = "%sSMRhdf/Qsmr-%s/%s/SCH_%s_%s%s_%s.ERR" %(l2dir,r[3],freq,r[0],r[1],orbit,str(r[2]).zfill(3))
    matfile = "%sSMRmat/Qsmr-%s/%s/%s%s.mat" %(l2dir,r[3],freq,r[5],orbit)
    errfile = "%sSMRmat/Qsmr-%s/%s/%s%s.qsmr_error" %(l2dir,r[3],freq,r[5],orbit)
    efile   = "/home/odinop/logs/%s.%s.%s.e" %(freq,orbit,r[3])
    ofile   = "/home/odinop/logs/%s.%s.%s.o" %(freq,orbit,r[3])

#clean up database: delete all records from this orbit,freqmod and version
c.execute("""DELETE level2 FROM level2,scans WHERE hex(orbit)=%s and calibration=%s and freqmode=%s and version=%s and scans.id=level2.id""",(orbit,cal,r[4],r[3]))

#add record in "Processed"
test = c.execute("""select prnr from Processed where hex(orbit)=%s and freqmode=%s and version=%s""",(orbit,freq,r[3]))
if test==0:
    c.execute("""insert into Processed (orbit,freqmode,version,prdate) values (cast(x%s as unsigned),%s,%s,now())""",(orbit,freq,r[3]))
else:
    c.execute("""update Processed set prnr=prnr+1,prdate=now() where hex(orbit)=%s and freqmode=%s and version=%s""",(orbit,freq,r[3]))

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
    test = c.execute("""select prnr from Processed where hex(orbit)=%s and freqmode=%s and version=%s""",(orbit,freq,r[3]))
    num = c.fetchone()
    if num[0]>MAX_NUMBER_OF_TRIES:
        mesg = sys.argv[0] + ": error can't open file - " + hdffile + "\nNot rerunning qsmr - STOP"
    else:
        mesg = sys.argv[0] + ": error can't open file - " + hdffile + "\nRerunning qsmr"
        launchcmd = "~/bin/odinlaunch start %s %s %s %s" % (orbit,orbit,freq,r[3])
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
        test = c.execute("""
INSERT delayed INTO level2
(version,id,latitude,longitude,mjd,date,sunZD,poffset)
SELECT %s,scans.id,%s,%s,%s,%s,%s,null
FROM scans
WHERE scans.freqmode=%s and hex(scans.orbit)=%s and scans.calibration=%s and scans.scan=%s;
""", (r[3],records[17],records[18],records[25],date,records[6],r[4],orbit,cal,records[8]))

vd.detach()               # "close" the vdata
vs.end()                  # terminate the vdata interface
f.close()                 # close the HDF file


#Read the matfiles
stdin,stdout, = os.popen4("~/hermod/mat/poff.sh " + matfile)
rawtext = stdout.read()
stdin.close()
stdout.close()
pat1=re.compile("!!,(.*),.*")
pat2=re.compile("!!,.*,(.*)")
scan = map(int,pat1.findall(rawtext))
poff = map(float,pat2.findall(rawtext))
poffpair=zip(scan,poff)
for i in poffpair:
    test = c.execute("""
update low_priority level2,scans set poffset=%s where calibration=%s and scan=%s and hex(orbit)=%s and freqmode=%s and level2.id=scans.id and version=%s;
""",(i[1],cal,i[0],orbit,r[4],r[3]))
    if glob.glob(errfile)!=[]:
        shutil.move(errfile,inffile)
    os.system("rm -f "+matfile)


