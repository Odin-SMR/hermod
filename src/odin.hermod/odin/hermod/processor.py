from MySQLdb import connect
from MySQLdb.cursors import DictCursor
import logging

from odin.hermod.hermodBase import connection_str
from odin.config.environment import set_hermod_logging
from pbs import GEMPbs
from torquepy import TorqueConnection

class ProcessorHandler:
    """Handles a set of transitions
    """

    def __init__(self, processors_ids):
        self.proclist = []
        torque_con = TorqueConnection('torque_host')
        already_inqueue = torque_con.inqueue('new')
        for p in processors_ids:
            if not "o%(orbit).4X%(calversion).1f%(fqid).2i%(version)s" %p in already_inqueue:
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

def main():
    set_hermod_logging()
    logger = logging.getLogger(__name__)
    logger.info('''looking for L1b-files to process''')
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
left join statusl2 s2 on (l1.id=s2.id and v.id=s2.fqid and v.qsmr=s2.version)
where v.active and l2f.id is null and l1.calversion=6 and (proccount is null or proccount<4)
order by orbit desc,fqid
limit 400
    '''
    query2 = '''
SELECT distinct l1.id,l1n.backend,l1n.orbit, v.id fqid, v.qsmr version, l1n.calversion, a.name, v.process_time FROM level1_new l1n
join level1 l1 using (orbit,backend,calversion)
join versions v on (v.fm=l1.freqmode and v.calversion=l1n.calversion)
join status on (l1.id=status.id)
join Aero a on (v.id=a.id)
where not exists
(select * from level2 l2 where l2.id=l1.id)
and exists (select count(*) cnt from level1b_gem l1bg where l1bg.id= l1.id group by l1bg.id having cnt>2)
and exists (select id from smrl1b_gem sl1bg where sl1bg.id=l1.id)
and not exists (select * from statusl2 s2 where s2.id=l1.id and s2.version=v.qsmr and s2.fqid=v.id and proccount>4)
and l1n.freqmode<>0 and v.active=1
order by l1n.orbit desc
limit 400
'''
    x = ProcHFactory(query2)
    print x
    logger.info('''submitting jobs to the queue''')
    x.submit()

if __name__=='__main__':

    main()

