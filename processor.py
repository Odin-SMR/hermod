#!/usr/bin/python2.5

from MySQLdb import connect
from MySQLdb.cursors import DictCursor

from hermod.hermodBase import connection_str
from pbs import GEMPbs

class ProcessorHandler:
    """Handles a set of transitions
    """

    def __init__(self, processors_ids):
        self.proclist = []
        for p in processors_ids:
            self.proclist.append(Processor(**p))

    def __repr__(self):
        s = ''
        for i in self.proclist:
            s = s + repr(i) +'\n'
        return s

    def submit(self,queue='new'):
        for i in self.proclist:
            i.set_submit_info(queue=queue)
            i.submit()

class Processor(GEMPbs):
    """A transition from a level1-object to a level2
    """

    def __init__(self,*arg,**kwargs):
        self.info = kwargs

    def __repr__(self):
        return 'Processor object: %(id)i, %(orbit)X, %(calversion)s, %(backend)s, %(version)s, %(fqid)i, %(process_time)s' %(self.info)

def ProcHFactory(sqlquery):
    """Factory returns a Processor handler from a sqlquery.

    The sql query is required to return (orbit,calversion,fqid,name,version,
    name,process_time,backend) to be put in a DictCursor
    """
    db = connect(**connection_str)
    cursor = db.cursor(DictCursor)
    cursor.execute(sqlquery)
    result =cursor.fetchall()
    cursor.close()
    db.close()
    return ProcessorHandler(result)



if __name__=='__main__':
    query = '''
 select distinct l1.id,l1.back backend,l1.orbit orbit,v.id fqid,v.qsmr version,
            l1.calversion,a.name,v.process_time
from (
select orbit,id,substr(backend,1,3) back,freqmode mode,calversion from level1
join status using (id)
join level1b_gem l1g using (id)
where status and l1g.filename regexp ".*HDF" and not locate(',',freqmode)
union
(
select orbit,id,substr(backend,1,3) back,substr(freqmode,1, locate(',',freqmode)-1) mode,calversion from level1
join status using (id)
join level1b_gem l1g using (id)
where status and l1g.filename regexp ".*HDF" and locate(',',freqmode)
)
union
(
select orbit,id,substr(backend,1,3) back,substr(freqmode from locate(',',freqmode)+1) mode,calversion from level1
join status using (id)
join level1b_gem l1g using (id)
where status and l1g.filename regexp ".*HDF" and locate(',',freqmode)
)) as l1
join versions v on (l1.mode=v.fm)
join Aero a on (v.id=a.id) 
left join level2files l2f on (l1.id=l2f.id and v.id=l2f.fqid and v.qsmr=l2f.version)
where v.active and l2f.id is null and l1.calversion=6
order by orbit desc,fqid   
    '''
    x = ProcHFactory(query)
    print x
    x.submit()

