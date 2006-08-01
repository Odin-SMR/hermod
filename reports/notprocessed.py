#!/usr/bin/python

import MySQLdb
import sys
import shutil
import os
import re
import glob,commands

#Connect to database
db=MySQLdb.connect(host="jet",user="odinuser",passwd="***REMOVED***",db="odin")

c = db.cursor(MySQLdb.cursors.SSDictCursor)
status=c.execute("""create temporary table allscans select
    orbit,freqmode,calibration,count(*) as cnt from scans group by
    orbit,freqmode,calibration""")

status=c.execute("""create temporary table procscans select
    orbit,freqmode,calibration,version,fqid,count(*) as cnt from scans natural join
    level2 group by orbit,freqmode,version,calibration,fqid""")
        
status=c.execute("""select allscans.freqmode, allscans.calibration,
    allscans.orbit, allscans.cnt as allcnt, procscans.cnt as
    proccnt,procscans.cnt/allscans.cnt as ratio, fqid, version from allscans left
    join procscans using (orbit, freqmode, calibration) """)

print c.description
row= c.fetchone()
while row<>None:
    try:
        if row['ratio'] is not None:
            print "%0.4X%5d%5d%7.2f%5d%5d%5d%7s" % (row['orbit'],row['freqmode'],row['calibration'],row['ratio'],row['proccnt'],row['allcnt'],row['fqid'],row['version'])
        else:
            print "%0.4X%5d%5d      -%5d    -    -      -" % (row['orbit'],row['freqmode'],row['calibration'],row['allcnt'])
        row = c.fetchone()
    except KeyboardInterrupt:
        sys.stderr.write("Break recieved\n")
        break
    except Exception,inst:
        sys.excepthook(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
        break

sys.stderr.write("Closing cursor...\n")
c.close()
db.close()
