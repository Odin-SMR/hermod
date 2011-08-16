#!/home/odinop/hermod_production_2.6/bin/python

from glob import glob
from odin.config.database import connect
from odin.config.environment import config,set_hermod_logging
from datetime import datetime
from os import remove,symlink
from os.path import join,basename,exists,dirname
from odin.ecmwf.ecmwf_nc import makedir
import logging

def main():
    set_hermod_logging()
    conf = config()
    log = logging.getLogger('link_SMRl1')
    db = connect()
    cur = db.cursor()
    cur2 = db.cursor()
    cur3 = db.cursor()
    log.info('Searching unlinked files')
    qsmr_name={}
    cur.execute('''SELECT distinct name,fm FROM Aero''')
    for n,k, in cur:
        qsmr_name[k]=n
    status = cur.execute("""
        select id,filename
        from level1b_gem
        left join smrl1b_gem using (id,filename)
        where filename regexp "^6.*" and linkname is null
        order by level1b_gem.date desc
        """)
    log.info('Found {0} unlinked files'.format(status))
    
    for id,filename in cur:
        full_path = join(conf.get('GEM','LEVEL1B_DIR'),filename)
        if not exists(full_path):
            cur2.execute('''
                    delete from level1b_gem
                    where id=%s and filename=%s''', (id,filename))
            print full_path
            continue
        cur2.execute('''
                select freqmode,calversion,backend from level1 where id=%s
                ''',id)
        for freqmode,calversion,backend in cur2:
            for fq in freqmode.split(','):
                if filename.endswith('PTZ') or filename.endswith('ZPT'):
                    rel_link = join (
                                   'V-{0}'.format(int(calversion)),
                                   'ECMWF',
                                   backend,
                                   basename(filename),
                               )
                else:
                    rel_link = join (
                                   'V-{0}'.format(int(calversion)),
                                   qsmr_name.get(int(fq),'invalid'),
                                   basename(filename),
                               )
                full_link = join(
                               conf.get('GEM','SMRL1B_DIR'),
                               rel_link,
                            )
                makedir(dirname(full_link))
                try:
                    symlink(full_path,full_link)
                except OSError,msg:
                    pass
                cur3.execute('''replace smrl1b_gem (id,filename,linkname) 
                                 values (%s,%s,%s) ''',(id,filename,rel_link))
    cur3.close()
    cur2.close()
    cur.close()
    db.close()
    log.info('Liked {0} files'.format(status))

if __name__=="__main__":
    main()
