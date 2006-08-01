#!/usr/bin/python

import MySQLdb
import sys

#Connect to database
db=MySQLdb.connect(host="jet",user="gem",db="odin")
c = db.cursor(MySQLdb.cursors.SSDictCursor)
status=c.execute("""select orbit,scans.freqmode,calibration,name,date from scans natural join level2 natural join Freqmodes order by orbit,freqmode,calibration,name""")
print c.description
row= c.fetchone()
print "header %i" %(1)
while row<>None:
    try:
        print "%0.4X%4i%4i%11s%21s" % (row['orbit'],row['freqmode'],row['calibration'],row['name'],row['date'])
        row = c.fetchone()
    except KeyboardInterrupt:
        print "Break recieved"
        break
    except Exception,inst:
        print "other error: ",inst
        print "error: ",sys.exc_info()[0]
        break

print "Closing cursor..."
c.close()
db.close()
