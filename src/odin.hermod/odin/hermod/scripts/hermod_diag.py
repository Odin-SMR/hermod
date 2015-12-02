
from subprocess import Popen,PIPE
from sys import argv

def execute_query(query):
    s =Popen(['mysql','-hmysqlhost','-ugem','smr','--table'],stdin=PIPE)
    s.stdin.write(query)
    s.stdin.close()

def last_l1b():
    '''old/hermodlastdays_l1b'''
    execute_query('''
SELECT date(start_utc) Observation,
hex(orbit) Orbit,
#hex(min(orbit)) start_orb,
#hex(max(orbit)) stop_orb,
#count(*) orbits,
level1.freqmode FreqMode,
level1.calversion L1bVer,
level1.attversion AttVer,
level1.nscans NScans,
#level1.processed Processed,
level1.filename Name,
level1.uploaded Uploaded,
#level1b_gem.filename Filename,
level1b_gem.date Date
FROM level1 JOIN level1b_gem USING (id)
WHERE level1.uploaded>'2010-09-01' OR level1b_gem.date>'2010-09-01'
#group by date(start_utc)
#ORDER by level1.uploaded asc
ORDER by level1b_gem.date asc
#order by start_utc asc
    ''')

def last_l2():
    '''old/hermodlastdays_l2.py'''
    execute_query('''
SELECT date(start_utc) Observation,
hex(orbit) Orbit,
#hex(min(orbit)) StartOrb,
#hex(max(orbit)) StopOrb,
#count(*) Orbits,
level1.freqmode L1bMode,
level1.calversion L1bVer,
#level1.processed L1b_Processed,
level1.uploaded L1b_Uploaded,
level2files.fqid L2Mode,
level2files.version L2Ver,
level2files.processed L2_Processed
FROM level2files,level1
where level1.id=level2files.id and level2files.processed>'2010-09-01'
#group by date(start_utc)
order by level2files.processed asc
#order by start_utc asc
''')

def last_ecmwf():
    '''old/hermodlastdays_ecmwf.py'''
    execute_query('''
SELECT date Date,
type Type,
hour Hour,
filename Name,
downloaded Downloaded
FROM ecmwf WHERE downloaded>'2010-09-01'
#group by date
#order by date asc
order by downloaded asc
    ''')


def list_ecmwf():
    '''old/hermodlist_ecmwf.py'''
    execute_query('''
SELECT date Date,
type Type,
hour Hour,
filename Name,
downloaded Downloaded
FROM ecmwf WHERE downloaded>'2001-07-01'
#group by date
order by date asc
#order by downloaded asc
    ''')
def list_l1b():
    '''old/hermodlist_l1b.py'''
    execute_query('''
SELECT date(start_utc) Observation,
hex(orbit) Orbit,
#hex(min(orbit)) start_orb,
#hex(max(orbit)) stop_orb,
#count(*) orbits,
level1.freqmode FreqMode,
level1.calversion L1bVer,
level1.attversion AttVer,
level1.nscans NScans,
#level1.processed Processed,
level1.filename Name,
level1.uploaded Uploaded,
#level1b_gem.filename Filename,
level1b_gem.date Date
FROM level1 JOIN level1b_gem using (id)
WHERE level1.uploaded>'2001-07-01'
#group by date(start_utc)
#order by level1.uploaded asc
order by start_utc asc
    ''')
def list_l1b_pdc():
    '''old/hermodlist_l1b_pdc.py'''

    execute_query('''
SELECT date(start_utc) Observation,
hex(orbit) Orbit,
#hex(min(orbit)) start_orb,
#hex(max(orbit)) stop_orb,
#count(*) orbits,
level1.freqmode FreqMode,
level1.calversion L1bVer,
level1.attversion AttVer,
level1.nscans NScans,
#level1.processed Processed,
level1.filename Name,
level1.uploaded Uploaded #,
##level1b_gem.filename Filename,
# level1b_gem.date Date
FROM level1 # JOIN level1b_gem using (id)
WHERE level1.uploaded>'2001-07-01'
#group by date(start_utc)
#order by level1.uploaded asc
order by start_utc asc
    ''')

def list_l1bzpt():
    '''old/hermodlist_l1bzpt.py'''
    execute_query('''

SELECT date, id, filename FROM level1b_gem WHERE date>'2001-07-01' ORDER BY id;
    ''')

def list_l2():
    '''old/hermodlist_l2.py'''

    execute_query('''
SELECT date(start_utc) Observation,
hex(orbit) Orbit,
#hex(min(orbit)) StartOrb,
#hex(max(orbit)) StopOrb,
#count(*) Orbits,
level1.freqmode L1bMode,
level1.calversion L1bVer,
#level1.processed L1b_Processed,
level1.uploaded L1b_Uploaded,
level2files.fqid L2Mode,
level2files.version L2Ver,
level2files.processed L2_Processed
FROM level2files,level1
where level1.id=level2files.id and level2files.processed>'2001-07-01'
#group by date(start_utc)
#order by level2files.processed asc
order by start_utc asc
    ''')
