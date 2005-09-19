#!/usr/bin/python

import MySQLdb
import sys
import shutil
import os
import re
import glob,commands

#Connect to database
db=MySQLdb.connect(user="odinuser",passwd="***REMOVED***",db="odin")

def usage():
    print """
    rerunOrbits restarts processing
    
    rerunOrbits orbit1 orbit2 calibration threshold
       orbit1 - first orbit number (hex)
       orbit2 - last orbit number
       freqmode - freqmode number, 0 is used for all.
       calibration - l1b calibration nr
       threshold - number of not processed scans to ignore
       
    examples:
        ./rerunOrbits.py 4000 40FF 21 6 20
  
    Executing this command would rerun all level1b files having freqmode 21 
    in calibration 6 which has more than 20 not processed scans in the 
    interval [4000,40Fq].
"""
                 
def main():
    a=0
    for i in sys.argv:
        a=a+1
        
    if a!=6:
        usage()
        sys.exit(str(a)+" :Not correct number of parameters")

    orbit1=sys.argv[1]
    orbit2=sys.argv[2]
    fq=sys.argv[3]
    cal=sys.argv[4]
    min=sys.argv[5]

    c=db.cursor()
    
    #find parameters in the database (Freqmodes,Currentversions)
    if fq!=0:
        status=c.execute("""select hex(orbit),freqmode,calibration,count(*) as cnt
        from scans
        left join level2 using (id)
        where level2.mjd is null and hex(orbit)<=%s and hex(orbit)>=%s and calibration=%s and freqmodeq=%s
        group by orbit,freqmode,calibration
        having cnt>%s""",(orbit2,orbit1,cal,fq,min))
    else:
        status=c.execute("""select hex(orbit),freqmode,calibration,count(*) as cnt
        from scans
        left join level2 using (id)
        where level2.mjd is null and hex(orbit)<=%s and hex(orbit)>=%s and calibration=%s
        group by orbit,freqmode,calibration
        having cnt>%s""",(orbit2,orbit1,cal,fq,min))

    #find orbit in the database (Freqmodes,Currentversions)
    res=c.fetchall()
    for o in res:
        status = c.execute("""select name,maxproctime from Freqmodes where freqmode=%s and active""",(o[1],))
        info = c.fetchall()
        if status==0:
            continue
        status = c.execute("""select qsmr from Currentversions where calibration=%s""",(o[2],))
        qsmr= c.fetchall()
        status = c.execute("""delete level2
                                from scans,level2
                                where hex(orbit)=%s and freqmode=%s 
                                    and calibration=%s
                                    and scans.id=level2.id""",(o[0],o[1],o[2]))

        print "delete %s %s %d" % (o[0],o[1],o[2])
        com = "cd /home/odinop/logs && echo \"~/bin/odinrun_Qsmr-%s %s %d %s\" | qsub -qstratos -l walltime=%s -N %s.%s.%s\n" % (qsmr[0][0],o[0],o[1],info[0][0],info[0][1],info[0][0],o[0],qsmr[0][0])
        print com
        stin,stou, = os.popen4(com)
        lines = stou.readlines()
        stin.close()
        stou.close()
  
   
if __name__ == "__main__":
    main()
