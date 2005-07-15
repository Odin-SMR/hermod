#!/usr/bin/python

import MySQLdb
import glob
import os
efile ="/home/odinop/logs/?M_AC*.e*"
ofile ="/home/odinop/logs/?M_AC*.o*"

#Connect to database
db=MySQLdb.connect(host="localhost",user="odinuser",passwd="***REMOVED***",db="odin")
c=db.cursor()

#read stderr/stdout


efiles = glob.glob(efile)
for i in efiles:
    efd=file(i)
    line=efd.readlines()
    text=str().join(line)
    name=i.split("/")
    param=name[4].split(".") 
    c.execute("""update Processed set stderr=%s where hex(orbit)=%s and freqmode=%s and version=%s""",(text,param[1],param[0],param[2]))
    efd.close()
    os.system("rm -f " + i)

ofiles = glob.glob(ofile)
for i in ofiles:
    ofd=file(i)
    line=ofd.readlines()
    text=str().join(line)
    name=i.split("/")
    param=name[4].split(".") 
    c.execute("""update Processed set stdout=%s where hex(orbit)=%s and freqmode=%s and version=%s""",(text,param[1],param[0],param[2]))
    ofd.close()
    os.system("rm -f " + i)
