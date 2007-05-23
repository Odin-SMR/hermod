from hermod.hermodBase import *
from hermod.session import *
import datetime
import os
import os.path
import re
import MySQLdb
import subprocess
import sys
import StringIO
from ftplib import FTP

ecmwfpat = re.compile('^.*([0-9]{6})\.([\d]{1,2})([A-Z]{1,2})\.gz')
'''
ecmwf interacts with nilumod to get weather data files from nilu
'''

class weatherfile:
    '''
    calls nilumod at zardoz.nilu.no to create the specified file. dowloads the file and adds a line in the ecmwf table
    '''
    def __init__(self,openDb,type,date):
        modes = {'T':'tz','Z':'tz','PV':'pv'}
        self.db = openDb
        self.type = type
        self.date = date
        self.filename =''
        self.hour = 0
        self.localname = os.path.join(config.get('GEM','ECMWF_DIR'),modes[type],date.strftime('%y%m'),date.strftime('ecmwf%y%m%d.0%%s.gz')%type)

    def generate(self):
        p = subprocess.Popen(['/usr/bin/ssh','murtagh@zardoz.nilu.no','/usr/sfw/bin/python','.odin/gen_%s.py'%self.type,self.date.strftime('%y%m%d')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=True)
        stdout,stderr, = p.communicate()
        self.filename =  stdout.rstrip()

    def download(self):
        f = FTP(config.get('NILU','host'),config.get('NILU','user'),config.get('NILU','passwd'))
        if not os.path.exists(os.path.dirname(self.localname)):
            try:
                os.makedirs(os.path.dirname(self.localname))
            except EnvironmentError,inst:
                print >> sys.stderr, inst.errno, inst.strerror, inst.filename
                sys.exit(1)
        status = f.retrbinary('RETR %s'%self.filename, open(self.localname, 'wb').write)

    def addDb(self):
        c = self.db.cursor()
        c.execute('''insert ecmwf (date,type,hour,filename) values (%s,%s,%s,%s) on duplicate key update downloaded=now(),filename=%s''',(self.date,self.type,self.hour,self.localname[len(config.get('GEM','ECMWF_DIR')):],self.localname[len(config.get('GEM','ECMWF_DIR')):]))
        c.close()

class weathercontrol:
    '''
    a data base reader, keeps track of what files we are missing
    '''
    def __init__(self,openDB,mode):
        self.db = openDB
        self.mode = mode

    def find(self):
        c = self.db.cursor()
        c.execute('''SELECT date FROM reference_calendar as r where not exists (select * from ecmwf as e where r.date=e.date and type=%s) and date<now() order by date''',(self.mode,))
        self.dates = [i[0] for i in c]
        c.close()

    def generate(self):
        for i in self.dates:
            if self.mode=="PV":
                c = weatherfile_PV(self.db,self.mode,i)
            else:
                c = weatherfile(self.db,self.mode,i)
            c.generate()
            if not c.filename=='':
                c.download()
                c.addDb()

class weatherfile_PV(weatherfile):
    def download(self):
        weatherfile.download(self)
        self.gen_lait()

    def gen_lait(self):
        lait = matlab(outputFile=open(os.path.expanduser('~/tmp/lait.log'),'w'),cwd=os.path.expanduser('~/Matlab/Odin_tools/'))
        lait.command("Odin_tools_startup")
        lait.command("convert_pv_to_mat_day(%s,'%s',1)"% (self.date.strftime('%Y,%m,%d'),os.path.join(config.get('GEM','ECMWF_DIR'),'pv/')))
        lait.close()
    
class ZPTfile:
    def __init__(self,opendb):
        self.db = opendb
        self.row = []
        pass

    def getNonExisting(self):
        cursor = self.db.cursor()
        cursor.execute('''SELECT id,filename from level1b_gem as l where not exists (select * from level1b_gem as m where m.id=l.id and m.filename regexp '.*ZPT' and  m.date>=l.date) and 
        filename regexp ".*LOG"''')
        self.row = [i for i in cursor]
        cursor.close()

    def genZPT(self,logfilepair):
        stringout = StringIO.StringIO()
        stringerr = StringIO.StringIO()
        x = matlab(cwd='/odin/extdata/ecmwf/tz',outputFile=stringout,errorFile=stringerr)
        x.command("create_tp_ecmwf_rss2('%s%s')"%(config.get('GEM','LEVEL1B_DIR'),logfilepair[1]))
        if stringerr.getvalue()<>'':
            sys.stderr.write(stringerr.getvalue())
        else:
            self.add(logfilepair)
        x.close()

    def genZPTs(self):
        for a in self.row:
            self.genZPT(a)

    def add(self,logfilepair):
        filepair = (logfilepair[0],logfilepair[1].replace('LOG','ZPT'))
        cursor = self.db.cursor()
        status = cursor.execute('''insert level1b_gem (id,filename) values (%s,%s) on duplicate key update date=now()''',filepair)
        cursor.close()

def getallexisting(top,db):
    c  = db.cursor()
    for root,dirs,files in os.walk(top):
        for name in files:
            mtch = ecmwfpat.match(name)
            if mtch is not None:
                filename = os.path.join(root,name)
                date = mtch.group(1)
                hour = mtch.group(2)
                type = mtch.group(3)
                mtime  = datetime.datetime.fromtimestamp(os.path.getmtime(filename))
                download = mtime.isoformat(' ')
                c.execute('''insert ignore ecmwf values (%s,%s,%s,%s,%s)''', (date,type,hour,download,filename[len(config.get('GEM','ECMWF_DIR')):]))

def filldatabase_tz():
    db = MySQLdb.connect(host=config.get('WRITE_SQL','host'), user=config.get('WRITE_SQL','user'), passwd=config.get('WRITE_SQL','passwd'), db='smr')
    getallexisting(os.path.join(config.get('GEM','ECMWF_DIR'),'tz'),db)
    db.close()

def filldatabase_pv():
    db = MySQLdb.connect(host=config.get('WRITE_SQL','host'), user=config.get('WRITE_SQL','user'), passwd=config.get('WRITE_SQL','passwd'), db='smr')
    getallexisting(os.path.join(config.get('GEM','ECMWF_DIR'),'pv'),db)
    db.close()

def fillcalendar():
    db = MySQLdb.connect(host=config.get('WRITE_SQL','host'), user=config.get('WRITE_SQL','user'), passwd=config.get('WRITE_SQL','passwd'), db='smr')
    c = db.cursor()
    date = datetime.date(2001,6,1)
    day = datetime.timedelta(1)
    while date<=datetime.date(2020,12,31):
        print date
        c.execute('''insert reference_calendar values (%s)''',(date.isoformat(),))
        date = date + day
    db.close()

def rungetfilesfromnilu():
    db = MySQLdb.connect(host=config.get('WRITE_SQL','host'), user=config.get('WRITE_SQL','user'), passwd=config.get('WRITE_SQL','passwd'), db='smr')
    t=weathercontrol(db,'T')
    t.find()
    t.generate()
    z=weathercontrol(db,'Z')
    z.find()
    z.generate()
    pv=weathercontrol(db,'PV')
    pv.find()
    pv.generate()
    db.close()

if __name__=='__main__':
    db = MySQLdb.connect(host=config.get('WRITE_SQL','host'), user=config.get('WRITE_SQL','user'), passwd=config.get('WRITE_SQL','passwd'), db='smr')
    x = ZPTfile(db)
    x.getNonExisting()
    x.genZPTs()
    db.close()
