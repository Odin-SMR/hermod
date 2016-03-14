from MySQLdb import connect
from MySQLdb.cursors import DictCursor
import logging

from odin.hermod.hermodBase import connection_str
from odin.config.environment import set_hermod_logging
from odin.config.environment import config as odin_config
from pbs import GEMPbs
from torquepy import TorqueConnection


class ProcessorHandler:
    """Handles a set of transitions
    """

    def __init__(self, processors_ids):
        self.proclist = []
        self.conf = odin_config()
        torque_con = TorqueConnection(self.conf.get("TORQUE", "torquehost"))
        already_inqueue = torque_con.inqueue('new')
        for p in processors_ids:
            if (not "o%(orbit).4X%(calversion).1f%(fqid).2i%(version)s" % p in
                    already_inqueue):
                self.proclist.append(Processor(**p))

    def __repr__(self):
        s = ''
        for i in self.proclist:
            s = s + repr(i) + '\n'
        return s

    def submit(self, queue='new'):
        for i in self.proclist:
            i.set_submit_info(queue=queue)
            i.submit()


class Processor(GEMPbs):
    """A transition from a level1-object to a level2
    """

    def __init__(self, *arg, **kwargs):
        self.info = kwargs

    def __repr__(self):
        return ('Processor object: %(id)i, %(orbit)X, %(calversion)s, ' +
                '%(backend)s, %(version)s, %(fqid)i, %(process_time)s' %
                (self.info))


def ProcHFactory(sqlquery):
    """Factory returns a Processor handler from a sqlquery.

    The sql query is required to return (orbit,calversion,fqid,name,version,
    name,process_time,backend) to be put in a DictCursor
    """
    db = connect(**connection_str)
    cursor = db.cursor(DictCursor)
    cursor.execute(sqlquery)
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return ProcessorHandler(result)


def main():
    set_hermod_logging()
    logger = logging.getLogger(__name__)
    logger.info('''looking for L1b-files to process''')
    query = '''
SELECT DISTINCT l1.id, l1.back backend, l1.orbit orbit, v.id fqid,
                v.qsmr version, l1.calversion, a.name, v.process_time
FROM (
    SELECT orbit, id, SUBSTR(backend, 1, 3) back, freqmode mode, calversion
    FROM level1
    JOIN level1b_gem l1g USING (id)
    WHERE l1g.filename REGEXP ".*HDF"
          AND NOT LOCATE(',',freqmode)
          AND level1.filename IS NOT NULL
          AND level1.filename != ''
    UNION
    (
    SELECT orbit, id, SUBSTR(backend, 1, 3) back,
           SUBSTR(freqmode, 1, LOCATE(',', freqmode) - 1) mode,
           calversion
    FROM level1
    JOIN level1b_gem l1g USING (id)
    WHERE l1g.filename REGEXP ".*HDF"
          AND LOCATE(',', freqmode)
          AND level1.filename IS NOT NULL
          AND level1.filename != ''
    )
    UNION
    (
    SELECT orbit, id, SUBSTR(backend, 1, 3) back,
           SUBSTR(freqmode from locate(',', freqmode) + 1) mode,
           calversion
    FROM level1
    JOIN level1b_gem l1g USING (id)
    WHERE l1g.filename REGEXP ".*HDF"
          AND LOCATE(',',freqmode)
          AND level1.filename IS NOT NULL
          AND level1.filename != ''
)) AS l1
JOIN versions v ON (CAST(l1.mode as UNSIGNED) = v.fm)
JOIN Aero a ON (v.id = a.id)
LEFT JOIN level2files l2f ON (l1.id = l2f.id AND v.id = l2f.fqid AND
                              v.qsmr = l2f.version)
LEFT JOIN statusl2 s2 ON (l1.id = s2.id AND v.id = s2.fqid AND
                          v.qsmr = s2.version)
WHERE v.active
      AND l2f.id IS NULL
      AND l1.calversion IN (6.0, 6.1, 7.0)
      AND (proccount IS NULL OR proccount < 4)
      AND v.calversion = l1.calversion
ORDER BY orbit DESC, fqid
LIMIT 400
'''
    x = ProcHFactory(query)
    print x
    logger.info('''submitting jobs to the queue''')
    x.submit()


if __name__ == '__main__':

    main()
