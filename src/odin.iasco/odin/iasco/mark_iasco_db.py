from datetime import date,timedelta
from MySQLdb import connect
from odin.config.environment import connection_str
from odin.config.gemlogger import timer
import logging
import logging.config
from pkg_resources import resource_stream

def markWinds(): 
    '''
    Find and mark the days where wind files have been updaten since the last assimilation
    '''
    name = config.get('logging','configfile')
    file = resource_stream('odin.config',name)
    logging.config.fileConfig(file)
    root_logger = logging.getLogger("")
    logger = logging.getLogger("mark_iasco_db")
    
    con = connect(**connection_str)
    query = """
        update iasco ia,ecmwf e set wind=1 
        where ia.assdate=e.date and e.downloaded>ia.processed
        """
    num_wind = con.query(query)
    con.close()
    logger.info(num_wind,'rows have been marked with wind flags')
    
def markL2(): 
    '''
    Find and mark the days where orbit files have been updaten since the last assimilation (limit: number_of_new_orbits/number_of_old_orbits>=0.5)
    '''
    name = config.get('logging','configfile')
    file = resource_stream('odin.config',name)
    logging.config.fileConfig(file)
    root_logger = logging.getLogger("")
    logger = logging.getLogger("mark_iasco_db")
    
    con =connect(**connection_str)
    query = """
        select T.date,T.fqid,T.version
        from (select date(start_utc) date, l2.fqid, l2.version, count(*) tot
        from level2files l2 ,level1 l1
        where l2.id=l1.id and ((fqid=3 and version='2-0') or (fqid=29 and version='2-1'))
        group by date(start_utc),fqid,version) T,(select distinct assdate date,fqid,version, count(distinct assdate,io.id) tot
        from iasco ia,iasco_orbits io
        where ia.assid=io.assid
        group by ia.assid,assdate,fqid,version
        order by assdate) S
        where T.date=S.date and T.fqid=S.fqid and T.version=S.version and (T.tot-S.tot)/S.tot>=.5
        """
    con.query(query)
    r = con.store_result()
    rows = r.fetch_row(0)
    for row in rows:
        q = """
            update iasco
            set hdf=1
            where assdate='%s' and fqid='%s' and version='%s'
            """ % row
        con.query(q)
    con.close()
    logger.info(len(rows),'rows have been marked with hdf flags')
    
def markAss(): 
    '''
    Find the days where wind and/or hdf is marked and marks assimilate on this day and 90 days ahead 
    '''
    name = config.get('logging','configfile')
    file = resource_stream('odin.config',name)
    logging.config.fileConfig(file)
    root_logger = logging.getLogger("")
    logger = logging.getLogger("mark_iasco_db")
    
    con = connect(**connection_str)
    query = """
        SELECT distinct rc.date,ia.fqid,ia.version
        FROM iasco ia, reference_calendar rc
        where hdf and rc.date between ia.assdate and adddate(ia.assdate,90)
        """
    con.query(query)
    r = con.store_result()
    rows = r.fetch_row(0)
    for row in rows:
        q = """
            update iasco
            set assimilate=1
            where assdate='%s' and fqid=%i and version='%s'
            """ % row
        con.query(q)
    query = """
        SELECT distinct rc.date
        FROM iasco ia, reference_calendar rc
        where wind and rc.date between ia.assdate and adddate(ia.assdate,90)
        """
    con.query(query)
    r = con.store_result()
    rows = r.fetch_row(0)
    for row in rows:
        q = """
            update iasco
            set assimilate=1
            where assdate='%s'
            """ % row
        con.query(q)
    con.close()
    logger.info('Assimilate flags have been added to rows with wind flags or hdf flags and 90 days ahead')

def markDaysWithNewOrbits():
    '''
    Find the days where new orbits have been processed (there were no orbits for this day when the assimilation were run the last time) and mark hdf and assimilate on this day and assimilate for 90 days ahead
    '''
    name = config.get('logging','configfile')
    file = resource_stream('odin.config',name)
    logging.config.fileConfig(file)
    root_logger = logging.getLogger("")
    logger = logging.getLogger("mark_iasco_db")
    
    con = connect(**connection_str)
    for fqid in [3,29]:
        if fqid==3: version='2-0'
        elif fqid==29: version='2-1'
        q1 = """
             SELECT distinct assdate 
             FROM iasco ia left join iasco_orbits io on (ia.assid=io.assid) 
             where fqid=%s and io.assid is null order by assdate
             """ % fqid
        con.query(q1)
        d = con.store_result()
        dates=d.fetch_row(0)
        for date in dates:     
            date=date[0]
            q2 = """
                 SELECT count(id) 
                 from level2files join level1 using (id) 
                 where (date(start_utc)='%s' or date(stop_utc)='%s') and fqid=%s and version='%s' 
                 """ % (date,date,fqid,version)
            con.query(q2)
            res = con.store_result()
            n=res.fetch_row(1)
            num=int(n[0][0])
            
            count = 0
            if not num==0:
                date90=date+timedelta(90)
                q3 = """
                     update iasco 
                     set hdf=1 where fqid=%s and assdate='%s'
                     """ % (fqid,date)
                q4 = """update iasco 
                     set assimilate=1 where fqid=%s and assdate between '%s' and '%s' 
                     """ % (fqid,date,date90)
                con.query(q3)
                con.query(q4)
                count = count + 1
    con.close()
    logger.info(count,'rows have been marked because new orbits have occured.')    

def main():
    markWinds()
    markL2()
    markAss()
    markDaysWithNewOrbits()

if __name__=="__main__":
    main()
