#!/usr/bin/python

import MySQLdb
import sys
import shutil
import os
import re
import glob,commands

#Connect to database
db=MySQLdb.connect(host="jet",user="odinuser",passwd="***REMOVED***",db="odin")
LEVEL1B_DIR="/odin/smr/Data/level1b/"
SMRl2_DIR="/odin/smr/Data/SMRl2/"
SMRl1b_DIR="/odin/smr/Data/SMRl1b/"

def usage():
    print """
    rerunOrbits restarts processing
    
    rerunOrbits orbit1 orbit2 modeid calibration threshold_ratio version
       orbit1 - first orbit number (hex)
       orbit2 - last orbit number
       modeid - , mode id - 0 is used for all.
       calibration - l1b calibration nr
       threshold_ratio - rerun if ratio (processedscans/totalscans) < threshold_ratio
       version - qsmr version
       
    examples:
        ./rerunOrbits.py 4000 40FF 29 6 .5 2-0
  
    Executing this command would rerun all level1b files having modeid 29 (SM_AC2ab) in
    calibration 6 which has more than 50% scans that are not processed in the
    interval [4000,40FF]. If 2-0 is a valid processor for that particular
    freqmode and calibration, jobs are sent to the queue.  """
                 
def main():
    
    #Checking for parameters
    if len(sys.argv)!=7: #missing or extra parameters -> end
        usage()
        sys.exit(sys.argv[0]+" :Not correct number of parameters")

    orbit1=int(sys.argv[1],16)
    orbit2=int(sys.argv[2],16)
    fqid=sys.argv[3]
    cal=sys.argv[4]
    min=sys.argv[5]
    qsmr=sys.argv[6]

    if float(min)>1.0001:
        usage()
        sys.exit(str(min)+" : The threshold ratio should be in [0..1]")

    c=db.cursor()
    print "Searching in database..."
    
    if fqid=="0": #all freqmodes
        status=c.execute("""select Freqmodes.freqmode,Freqmodes.fqid,name,maxproctime,prefix,backend from Freqmodes natural join Versions where qsmr=%s""",(qsmr,))
    else:
        status=c.execute("""select Freqmodes.freqmode,Freqmodes.fqid,name,maxproctime,prefix,backend from Freqmodes natural join Versions where qsmr=%s and Freqmodes.fqid=%s""",(qsmr,fqid))
    modes = c.fetchall()
    
    for mode in modes:
        fqmode = mode[0]
        fmid   = mode[1]
        name   = mode[2]
        mtime = mode[3]
        pfix = mode[4]
        back = mode[5]
        print "Mode: " + name
        status=c.execute("""create temporary table allscans 
                                select orbit,freqmode,calibration,count(*) as cnt 
                                from scans 
                                where orbit<=%s and orbit>=%s 
                                    and calibration=%s 
                                    and freqmode=%s  
                                group by orbit,freqmode,calibration""",(orbit2,orbit1,cal,fqmode))
        status=c.execute("""create temporary table procscans 
                                select orbit,freqmode,calibration,version,fqid,count(*) as cnt 
                                from scans natural join level2
                                where orbit<=%s 
                                    and orbit>=%s
                                    and version=%s 
                                    and calibration=%s 
                                    and fqid=%s
                                    and freqmode=%s
                                group by orbit,freqmode,version,calibration,fqid""",(orbit2,orbit1,qsmr,cal,fmid,fqmode))
        
        status=c.execute("""select allscans.orbit,procscans.cnt/allscans.cnt as ratio 
                            from allscans left join procscans using (orbit,freqmode,calibration)
                            having ratio<%s or ratio is null""",(min,))

        if status==0:
            print "No orbits were found in this mode"
            continue

        print "Found %d processes to reprocess" %(status)

        res=c.fetchall()
        status = c.execute("""drop table allscans""")
        status = c.execute("""drop table procscans""")
    
        for o in res: #loop over all orbits found in above selection
            orbit= o[0]
            orb = hex(orbit)[2:].upper().zfill(4)
            print "Processing orbit %s" %(orb)
            print "    deleting scans in level2 table"

            status = c.execute("""delete level2
                                    from scans,level2
                                    where orbit=%s and freqmode=%s 
                                        and calibration=%s
                                        and version=%s
                                        and fqid=%s
                                        and scans.id=level2.id""",(orbit,fqmode,cal,qsmr,fmid))
            print "      %d profiles removed" %(status)
            print "    creating and linking zpt-file"
            linkcom = "ln -sf %sV-%s/%s/%s/%s%s.ZPT /odin/smr/Data/SMRl1b/V-%s/ECMWF/%s/%s%s.ZPT" %(LEVEL1B_DIR,str(cal),back,orb[:2],pfix,orb,str(cal),back,pfix,orb)
            zptcom ="~/bin/create_tp_ecmwf_rss2 %sV-%s/%s/%s/%s%s.LOG" %(LEVEL1B_DIR,cal,back,orb[:2],pfix,orb)
            #execute zptcom
            os.system(zptcom)
            #execute linkcom
            stin,stou,sterr, = os.popen3(linkcom)
            lines = stou.readlines()
            for i in sterr.readlines():
                info = "  - %s" %(i)
                sys.stdout.write(info)
            stin.close()
            stou.close()
            sterr.close()
        
            print "    removing old .mat file"
            rmcom ="/bin/rm -f %s" %(genMat(name,orb,pfix,qsmr))
            stin,stou,sterr, = os.popen3(rmcom)
            for i in sterr.readlines():
                info = "  - %s" %(i)
                sys.stdout.write(info)
            sterr.close()
            stin.close()
            stou.close()
        
            print "    sending job to queue"
            com = "cd /home/odinop/logs && echo \"~/bin/odinrun_Qsmr-%s %s %s %s\" | qsub -qstratos -l walltime=%s -N %s.%s.%s\n" % (qsmr,orb,cal,name,mtime,name,orb,qsmr)
            stin,stou,sterr, = os.popen3(com)
            for i in sterr.readlines():
                info = "    - %s" %(i)
                sys.stdout.write(info)
            sterr.close()
            stin.close()
            stou.close()
            print
  
def genSMRL1bDir(fmname,cal):
    dir = "%sV-%d/%s/" %(SMRL1B_DIR,cal,fmname)
    return dir

def genMat(fmname,orb,prefix,qsmr):
    filename = "%sSMRmat/Qsmr-%s/%s/%s%s.mat" %(SMRl2_DIR,qsmr,fmname,prefix,orb)
    return filename
                                
if __name__ == "__main__":
    main()
