#!/usr/bin/python
# coding: UTF-8

import MySQLdb 
import sys
import logger
import logger.config
from odin.config.environment import *
from convert_date import utc2mjd
from datetime import datetime,timedelta

def w2iasco(date,fqid,version):
    """
    Write information to the iasco database.
    """
    logger.config.fileConfig("/home/zakrisso/hermod/src/odin.config/odin/config/odinlogger.cfg")
    logger = logging.getLogger("iasco_database")
    
    if fqid==29:
        species=['O3_501','N2O']
    elif fqid==3:
        species=['O3_544','H2O','HNO3']
    
    db = MySQLdb.connect(host=config.get('WRITE_SQL','host'), user=config.get('WRITE_SQL','user'), passwd=config.get('WRITE_SQL','passwd'), db='smr')
    for spec in species:
        year,month,day=date.year,date.month,date.day
        assdate=date
        date_mjd=utc2mjd(year,month,day)
        assfile=spec + '/' + str(year) + '/' + str(month) + '/' + spec + '_' + str(date_mjd) + '_00.mat'
        processed=datetime.now()

        ch = db.cursor()
        status=ch.execute('''SELECT * from iasco where assdate=%s and species=%s ''',(assdate,spec)) # Check if there are some information in the iasco database for the specific date and species
        ch.close()
        if status==0: # No information => the species is never assimilated for this day
            new = db.cursor()
            new.execute('''INSERT iasco (fqid,processed,assfile,assdate,species,version) values (%s,%s,%s,%s,%s,%s)''',(fqid,processed,assfile,assdate,spec,version))# Insert new data for the specific assid
            new.close()
        elif status==1: # Existing information => The species has been assimilated for this day before, but there have been an update in wind-data or in the tracer field 
            ins = db.cursor()
            ins.execute('''UPDATE iasco set processed=now(),wind=0,hdf=0,assimilate=0 where assdate=%s and species=%s ''',(assdate,spec)) # Update the time of processing to now and set all booleans to 0
            ins.close()
    logger.info('The IASCO database have been updated for date:',date,'and fqid',fqid) # Write to logg

def w2iasco_orbits(date,assid,l1ids):
    """
    Write information to the iasco_orbits database.
    """
    if l1ids==[]:
        sys.exit('Failed in db_write.orbit, there are no l1id' + '\nDate:' + str(date) + '\nAssid:' + str(assid) + '\nL1ids:' + str(l1ids))
    else:   
        db = MySQLdb.connect(host=config.get('WRITE_SQL','host'), user=config.get('WRITE_SQL','user'), passwd=config.get('WRITE_SQL','passwd'), db='smr')
        d = db.cursor()
        d.execute('''DELETE from iasco_orbits where assid=%s''',assid)
        d.close()
        for l1id in l1ids: 
            ins = db.cursor()
            ins.execute('''INSERT iasco_orbits (assid,id) values (%s,%s)''',(assid,l1id)) # Insert level 1 id and corresponding assid 
            ins.close()
    
def getStartDate():
    """
    Get the date where to start the assimilation. The main program (blackbox_main.py) loops over all days from this date until today.
    """
    db = MySQLdb.connect(host=config.get('WRITE_SQL','host'), user=config.get('WRITE_SQL','user'), passwd=config.get('WRITE_SQL','passwd'), db='smr')
    mi = db.cursor(MySQLdb.cursors.DictCursor)
    mi.execute('''SELECT MIN(assdate) assdate from iasco where wind or hdf or assimilate ''')
    mi.close()    
    date=[v['assdate'] for v in mi]
    if not date[0]==None:
        return date[0]
    else: return False

def getNewDates():
    """
    Get the days that never been assimilated before. These are the dates from the last day that has been assimilated until the last day where it exists wind data.
    """
    db = MySQLdb.connect(host=config.get('WRITE_SQL','host'), user=config.get('WRITE_SQL','user'), passwd=config.get('WRITE_SQL','passwd'), db='smr')

    la = db.cursor()
    la.execute('''select min(a.assdate) from 
                (select MAX(assdate) assdate from iasco where fqid=3
                union select MAX(assdate) assdate from iasco where fqid=29) a ''') # Last day that has been assimilated
    la.close()
    latest_assimilated=[i[0] for i in la]
    latest_assimilated[0]=latest_assimilated[0]+timedelta(1) # Don't assimilate the last day twice
    
    lwd = db.cursor()
    lwd.execute('''SELECT MAX(date) from ecmwf where type in ('U','V') ''') # Last day with wind data
    lwd.close()
    latest_wind_date=[i[0] for i in lwd]
    latest_wind_date[0] = latest_wind_date[0]-timedelta(1)

    new_dates=[]
    diff=latest_wind_date[0]-latest_assimilated[0]
    for j in range(0,diff.days+1):
        new_dates.append(latest_assimilated[0]+timedelta(j))
    return new_dates
    
def getWindBool(date,fqid):
    """
    Collect information from the iasco database to decide if the assimilation process for an update in a wind file should be run for the fqid on this day.
    """
    db = MySQLdb.connect(host=config.get('WRITE_SQL','host'), user=config.get('WRITE_SQL','user'), passwd=config.get('WRITE_SQL','passwd'), db='smr')
    cur = db.cursor(MySQLdb.cursors.DictCursor)
    wind=cur.execute('''SELECT * from iasco where wind and assdate=%s and fqid=%s''',(date,fqid))
    cur.close()
    if wind: return True
    else: return False
    
def getHdfBool(date,fqid):
    """
    Collect information from the iasco database to decide if the assimilation process for an update in a tracer field file should be run for the fqid on this day.
    """
    db = MySQLdb.connect(host=config.get('WRITE_SQL','host'), user=config.get('WRITE_SQL','user'), passwd=config.get('WRITE_SQL','passwd'), db='smr')
    cur = db.cursor(MySQLdb.cursors.DictCursor)
    hdf=cur.execute('''SELECT *  from iasco where hdf and assdate=%s and fqid=%s''',(date,fqid))
    cur.close()
    if hdf: return True
    else: return False
    
def getAssimilateBool(date,fqid):
    """
    Collect information from the iasco database to decide if the assimilation process should be run for the fqid on this day.
    """
    db = MySQLdb.connect(host=config.get('WRITE_SQL','host'), user=config.get('WRITE_SQL','user'), passwd=config.get('WRITE_SQL','passwd'), db='smr')
    cur = db.cursor(MySQLdb.cursors.DictCursor)
    assim=cur.execute('''SELECT *  from iasco where assimilate and assdate=%s and fqid=%s''',(date,fqid))
    cur.close()
    if assim: return True
    else: return False
    
def getAssid(date,fqid):
    """
    Get all the assids for the specific fqid and date. There should be 2 assids for fqid=29 and 3 for fqid=3.
    """
    db = MySQLdb.connect(host=config.get('WRITE_SQL','host'), user=config.get('WRITE_SQL','user'), passwd=config.get('WRITE_SQL','passwd'), db='smr')
    a_id = db.cursor(MySQLdb.cursors.DictCursor)
    a_id.execute('''SELECT assid from iasco where assdate=%s and fqid=%s''',(date,fqid))
    a_id.close()
    assids=[i['assid'] for i in a_id]
    return assids

def getOrbitInfo(date,fqid,version):
    """
    Get information about the orbits that are used to produce the tracer fields.
    """
    db = MySQLdb.connect(host=config.get('WRITE_SQL','host'), user=config.get('WRITE_SQL','user'), passwd=config.get('WRITE_SQL','passwd'), db='smr')
    cur = db.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('''SELECT distinct orbit,date(start_utc) start_utc,date(stop_utc) stop_utc,id from level2 join level1 using (id) where (date(start_utc)=%s or date(stop_utc)=%s) and fqid=%s and version2=%s order by start_utc''',(date,date,fqid,version))
    cur.close()
    orbit,start_utc,stop_utc,l1id=[],[],[],[]
    for i in cur:
        orbit.append(int(i['orbit']))
        start_utc.append(i['start_utc'])
        stop_utc.append(i['stop_utc'])
        l1id.append(i['id'])
    orbit_list={'orbit':orbit, 'start_utc':start_utc, 'stop_utc':stop_utc, 'l1id':l1id}
    if orbit_list['orbit']==[] or orbit_list['l1id']==[]:
        sys.exit('Failed with achiving an orbit list in program db_calls.getOrbitInfo' + '\nDate:' + str(date) + '\nOrbit_list:' + str(orbit_list))
    else:
        return orbit_list
