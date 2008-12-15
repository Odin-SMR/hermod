#!/usr/bin/python

from os import symlink
from os.path import basename,join

from MySQLdb import connect
from MySQLdb.cursors import DictCursor

from hermod.hermodBase import config,connection_str


def relink(start,stop):
    i = range(start,stop,0x100)
    db = connect(**connection_str)
    cursor = db.cursor(DictCursor)
    for st,sp in zip(i[:-1],i[1:]):
        cursor.execute('''
            select distinct l1.id,a.backend,l1.orbit,
                l1.calversion,a.name,l1bg.filename
            from level1 l1
            join level0_raw l0 on (l1.orbit>=floor(l0.start_orbit) 
                and l1.orbit<=floor(l0.stop_orbit))
            join level1b_gem l1bg on (l1bg.id=l1.id)
            join Aero a on (a.mode=l0.setup and a.backend=l1.backend)
            join versions v on (a.id=v.id and l1.calversion=v.calversion)
            left join level2files l2f on (l1.id=l2f.id and a.id=l2f.fqid and v.qsmr=l2f.version)
            where l1.calversion=6 and l1.orbit>=%s and l1.orbit<=%s
            ''',(st,sp))
        for i in cursor:
            base = basename(i['filename'])
            src = join(config.get('GEM','LEVEL1B_DIR'),i['filename'])
            if i['filename'].endswith('ZPT'):
                trg = join(config.get('GEM','SMRL1B_DIR'),'V-%(calversion)i','ECMWF','%(backend)s',base) % i
            else:
                trg = join(config.get('GEM','SMRL1B_DIR'),'V-%(calversion)i','%(name)s',base) % i
            try:
                #print "ln -s", src,trg
                symlink(src,trg)
            except OSError, inst:
                print inst
                print src, trg
                continue
            print "%s OK" %trg
    cursor.close()
    db.close()

if __name__ == '__main__':
    relink(0x0,0xA000)