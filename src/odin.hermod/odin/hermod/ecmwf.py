from odin.config.environment import HermodError,HermodWarning,config
import datetime
import os
import os.path
import re
import MySQLdb
import subprocess
import sys
from ftplib import FTP
from os.path import exists,join
from interfaces import IMakeZPT
from session import GEMMatlab

ecmwfpat = re.compile('^.*([0-9]{6})\.([\d]{1,2})([A-Z]{1,2})\.gz')
'''
ecmwf interacts with nilumod to get weather data files from nilu
'''

config = config()

class weatherfile:
    '''calls nilumod at zardoz.nilu.no to create the specified file. 
    downloads the file and adds a line in the ecmwf table
    '''
    def __init__(self,openDb,type,hour,date):
        modes = {'T':'tz','Z':'tz','PV':'pv','U':'tzuv','V':'tzuv'}
        self.db = openDb
        self.type = type
        self.date = date
        self.filename =''
        self.hour = '%02d' %hour
        if (self.type == 'U') or (self.type == 'V'):
            self.localname = join(config.get('GEM','ECMWF_DIR'),
                    modes[type],date.strftime('%y%m'),
                    date.strftime('ecmwf%y%m%d.%%s.-1.%%s.gz')%(type,
                            self.hour)
                    )
        elif (self.type == 'T') or (self.type == 'Z') or (self.type == 'PV'):
            self.localname = join(config.get('GEM','ECMWF_DIR'),
                    modes[type],date.strftime('%y%m'),
                    date.strftime('ecmwf%y%m%d.0%%s.gz')%type
                    )
					
    def generate(self):
        p = subprocess.Popen(
                [
                    '/usr/bin/ssh',
                    'murtagh@zardoz.nilu.no',
                    '/usr/sfw/bin/python',
                    '.odin/gen_%s.py'%self.type,self.date.strftime('%y%m%d'),
                    self.hour
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,close_fds=True)
        stdout,stderr, = p.communicate()
        self.filename =  stdout.rstrip()
                
    def download(self):
        f = FTP(config.get('NILU','host'),config.get('NILU','user'),
                config.get('NILU','passwd'))
        if not os.path.exists(os.path.dirname(self.localname)):
            try:
            	os.makedirs(os.path.dirname(self.localname))
            except EnvironmentError,inst:
                print >> sys.stderr, inst.errno, inst.strerror, inst.filename
                sys.exit(1)
        status = f.retrbinary('RETR %s'%self.filename, 
                open(self.localname, 'wb').write)

    def addDb(self):
        c = self.db.cursor()
        date_new = datetime.date(int(self.date.strftime('%Y')),
                int(self.date.strftime('%m')),int(self.date.strftime('%d')))
        c.execute('''insert ecmwf (date,type,hour,filename) values 
                (%s,%s,%s,%s) on duplicate key update downloaded=now(),
                filename=%s''',(date_new,self.type,self.hour,
                self.localname[len(config.get('GEM','ECMWF_DIR')):],
                self.localname[len(config.get('GEM','ECMWF_DIR')):]))
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
        if self.mode == 'U' or self.mode == 'V':
            c.execute('''
                    SELECT date,time 
                    FROM reference_calendar,reference_time 
                    where not exists (
                        select date,hour 
                        from ecmwf 
                        where reference_calendar.date=ecmwf.date 
                            and reference_time.time=ecmwf.hour 
                            and type=%s) 
                        and date<now() order by date desc limit 160''',
                    (self.mode,))
            self.dates = [i[0] for i in c]
            self.hour = [i[1] for i in c]
        elif self.mode == 'T' or self.mode == 'Z' or self.mode == 'PV':	
            c.execute('''
                    SELECT date 
                    FROM reference_calendar as r 
                    where not exists (
                        select * 
                        from ecmwf as e 
                        where r.date=e.date and type=%s) 
                        and date<now() order by date''',
                    (self.mode,))
            self.dates = [i[0] for i in c]
            self.hour = [0 for i in c]

            # If wind-files should be downloaded for 0,6,12,18 hours instead of
            # just 0, the if-statement is unnecessary and c.execute, self.dates
            # and self.hour should be defined as in the case of U and V for all
            # the modes.

        c.close()

    def generate(self):
        for date,hour in zip(self.dates,self.hour):
            if self.mode=="PV":
                c = weatherfile_PV(self.db,self.mode,hour,date)
            else:
                c = weatherfile(self.db,self.mode,hour,date)
            c.generate()
            if not c.filename =='':
                c.download()
                c.addDb()

class weatherfile_PV(weatherfile,GEMMatlab):
    def download(self):
        weatherfile.download(self)
        self.gen_lait()

    def gen_lait(self):
        self.start_matlab()
        self.matlab_command('cd ~/Matlab/Odin_tools/')
        self.matlab_command("Odin_tools_startup")
        self.matlab_command("convert_pv_to_mat_day(%s,'%s',1)"\
                %(self.date.strftime('%Y,%m,%d'),
                os.path.join(config.get('GEM','ECMWF_DIR'),'pv/')))
        self.close_matlab()
    

class MatlabMakeZPT(IMakeZPT):
    """ implementation with MATLAB as generator
    """

    def makeZPT(self):
        if hasattr(self,'m_session'):
            if hasattr(self,'zpt'):
                prefix = config.get('GEM','LEVEL1B_DIR')
                self.m_session.matlab_command('cd /odin/extdata/ecmwf/tz')
                self.m_session.matlab_command(
                        "create_tp_ecmwf_rss2('%s')"%join(prefix,self.log))
                return self.zpt
        else: 
            raise HermodError('No Matlab-session started')
    
    def checkIfValid(self,opendb):
        db_OK = False
        file_OK = False
        prefix = config.get('GEM','LEVEL1B_DIR')
        cursor = opendb.cursor()
        status = cursor.execute('''
            SELECT id,filename 
            from level1b_gem as l 
            where not exists (
                select * 
                from level1b_gem as m 
                where m.id=l.id and m.filename regexp '.*ZPT' 
                    and  m.date>=l.date)
                and filename regexp ".*LOG" and id=%s''',self.id)
        if status==0:
            db_OK=True
        if hasattr(self,'zpt'):
            if exists(join(prefix,self.zpt)):
                file_OK =True
        cursor.close()
        return file_OK and db_OK
                


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
                c.execute('''insert ignore ecmwf values (%s,%s,%s,%s,%s)''', (date_new,type,hour,download,filename[len(config.get('GEM','ECMWF_DIR')):]))

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
    db = MySQLdb.connect(host=config.get('WRITE_SQL','host'), 
            user=config.get('WRITE_SQL','user'), 
            passwd=config.get('WRITE_SQL','passwd'), db='smr')
    t=weathercontrol(db,'T')
    t.find()
    t.generate()
    z=weathercontrol(db,'Z')
    z.find()
    z.generate()
    pv=weathercontrol(db,'PV')
    pv.find()
    pv.generate()
    u=weathercontrol(db,'U')
    u.find()
    u.generate()
    v=weathercontrol(db,'V')
    v.find()
    v.generate()
    db.close()
if __name__=='__main__':
    db = MySQLdb.connect(host=config.get('WRITE_SQL','host'), user=config.get('WRITE_SQL','user'), passwd=config.get('WRITE_SQL','passwd'), db='smr')
    x = ZPTfile(db)
    x.getNonExisting()
    x.genZPTs()
    db.close()


