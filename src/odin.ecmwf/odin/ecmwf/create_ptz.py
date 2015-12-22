import logging
from odin.config.environment import set_hermod_logging, config
from odin.config.database import connect
from odin.ecmwf.donalettyEcmwfNC import ZptFile
from os.path import join


def main():
    conf = config()
    set_hermod_logging()
    db = connect()
    cur1 = db.cursor()
    cur2 = db.cursor()
    log = logging.getLogger(__name__)
    log.info('Searching for HDF-files without PTZ-files')
    status = cur1.execute('''
          SELECT l1g.id,l1g.filename
            from level1b_gem l1g,level1
            where l1g.id=level1.id
                and l1g.filename regexp ".*HDF"
                and level1.start_utc>"2011-05-01"
                and not exists (
                    select * from level1b_gem s
                    where s.filename regexp ".*PTZ"
                        and l1g.id=s.id)
                and exists (
                    select * from ecmwf e
                    where e.date=date(level1.start_utc) and e.type='AN')
                and l1g.filename regexp "^(6\.0).*"
          UNION
          SELECT l1g.id,l1g.filename
            from level1b_gem l1g,level1
            where l1g.id=level1.id
                and l1g.filename regexp ".*HDF"
                and not exists (
                    select * from level1b_gem s
                    where s.filename regexp ".*PTZ"
                        and l1g.id=s.id)
                and exists (
                    select * from ecmwf e
                    where e.date=date(level1.start_utc) and e.type='AN')
                and l1g.filename regexp "^(6\.1|7\.0).*"
            order by id desc
            limit 600;
    ''')
    log.info('Found {0} HDF-files with coresponding AN.NC-files'.format(
        status))
    for f in cur1:
        hdffile = join(conf.get('GEM', 'LEVEL1B_DIR'), f[1])
        logfile = hdffile.replace('HDF', 'LOG')
        ptzfile = logfile.replace('LOG', 'PTZ')
        ZptFile(logfile, ptzfile)
        query = '''
                replace level1b_gem
                (id, filename)
                values (%s, "%s");
                ''' % (f[0], f[1].replace('HDF', 'PTZ'))
        status = cur2.execute(query)
        log.info('Tried query {0} with status {1}'.format(query, status))
        print 'Tried query {0} with status {1}'.format(query, status)
    cur1.close()
    cur2.close()
    db.close()


if __name__ == "__main__":
    main()
