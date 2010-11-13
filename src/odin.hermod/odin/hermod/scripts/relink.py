#!/usr/bin/python

from os import symlink
from os.path import basename,join

from MySQLdb import connect
from MySQLdb.cursors import DictCursor

from odin.hermod.hermodBase import config,connection_str


def relink():
    
    db = connect(**connection_str)
    it_cursor = db.cursor()
    it_cursor.execute('''SELECT distinct orbit FROM level1b_gem l1bg, level1 l1  where l1bg.date > now() - interval 2 day and l1bg.id=l1.id order by date desc''')

    
    cursor = db.cursor(DictCursor)
    for orb in it_cursor:
        cursor.execute('''
select distinct a.name,l1.calversion,l1.backend,l1.orbit,filename
            from (
select orbit,id,substr(backend,1,3) backend,freqmode mode,calversion,l1g.filename from level1
join status using (id)
join level1b_gem l1g using (id)
where status and not locate(',',freqmode)
union
(
select orbit,id,substr(backend,1,3) backend,substr(freqmode,1, locate(',',freqmode)-1) mode,calversion,l1g.filename from level1
join status using (id)
join level1b_gem l1g using (id)
where status  and locate(',',freqmode)
)
union
(
select orbit,id,substr(backend,1,3) backend,substr(freqmode from locate(',',freqmode)+1) mode,calversion, l1g.filename from level1
join status using (id)
join level1b_gem l1g using (id)
where status  and locate(',',freqmode)
)) as l1
join versions v on (l1.mode=v.fm)
join Aero a on (v.id=a.id) and l1.orbit=%s
            ''',orb)
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
    it_cursor.close()
    db.close()

if __name__ == '__main__':
    relink()
