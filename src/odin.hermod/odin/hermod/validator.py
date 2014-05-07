#!/usr/bin/python2.5
from MySQLdb import connect
from odin.hermod.hermodBase import connection_str,config
from os.path import exists,join
from os import walk
from re import compile

def level1b_disk():
    """check and delete if all registered files in level1b_gem exists
    on disk.
    """
    bad = []
    db = connect(**connection_str)
    cursor = db.cursor()
    cursor.execute('''select id,filename from level1b_gem''')
    for (id,file) in cursor:
        if not exists(join(config.get('GEM','LEVEL1B_DIR'),file)):
            print id,file
            bad.append((id,file))
    cursor.executemany('''delete level1b_gem where id=%s and filename=%s''',
            bad)
    cursor.close()
    db.close()

def level1_database(dir):
    """check and delete if all files disk exists in database.
    """
    log = open('notindb.txt','wb')
    #pattern = compile('^.*/(([\d].[\d])/(AC1|AC2|FBA)/.{2}/O[BCD]1B[\w]\.(ZPT|LOG|HDF))')
    pattern = compile('^.*/(([\d].[\d])/(AC1|AC2|FBA).*([\w]{4})\.(ZPT|LOG|HDF))')
    db = connect(**connection_str)
    cursor = db.cursor()
    for root,dirs,files in walk(dir):
        for f in files:
            file = join(root,f)
            m = pattern.match(file)
            if m is not None:
                i = cursor.execute('''select * from level1b_gem where filename=%s  ''',(m.groups()[0]))
                if i==0:
                    print >>log, file
    log.close()
    cursor.close()
    db.close()
