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
        return 'Processor object: %(orbit)X, %(calversion)s, %(backend)s, %(version)s, %(fqid)i' %(self.info)

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
    sqlquery= ('''
    select distinct l1.id,a.backend,l1.orbit,a.id as fqid,v.qsmr version,
        l1.calversion,a.name,v.process_time
    from level1 l1
    join orbitmeasurement om on (l1.id=om.l1id)
    join level0_raw l0 on (l0.id=om.l0id)
    join level1b_gem l1bg on (l1bg.id=l1.id)
    join Aero a on (a.mode=l0.setup and a.backend=l1.backend)
    join versions v on (a.id=v.id and l1.calversion=v.calversion)
    left join level2files l2f on (l1.id=l2f.id and a.id=l2f.fqid and v.qsmr=l2f.version)
    where v.active and (l1.uploaded>l2f.processed or l2f.processed is null) 
        and l1.orbit>=0x8000  and l1.orbit<=0x9000
    order by orbit desc, backend
    limit 1000
    ''')
    x = ProcHFactory(sqlquery)
    print x
    x.submit()



