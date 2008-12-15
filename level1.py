from MySQLdb import connect
from MySQLdb.cursors import DictCursor
from os import makedirs,walk
from os.path import join,basename,dirname,splitext,exists
from hermod.hermodBase import config,connection_str,HermodError,HermodWarning
from subprocess import Popen,PIPE
from pexpect import spawn,EOF
from re import compile
from os import stat,system,symlink
from stat import ST_MTIME
from datetime import datetime
from sys import stderr
from pdc import PDCkftpGetFiles,PDCKerberosTicket
from ecmwf import MatlabMakeZPT
from session import GEMMatlab
from gemlogger import logger

class Level1Handler:
    """A class that handles a set of level1 idetifiers
    """

    def __init__(self,ids_list):
        self.ids = ids_list

class Level1:
    """A class to handle one level1 attributes
    """

    def __init__(self,database_id):
        self.id = database_id

def fromkeys(orbit,backend,calversion,db):
    """
    Return a Level1-object from the key
    """
    cursor = db.cursor()
    status=cursor.execute('''
        select id 
        from level1
        where orbit=%s and backend=%s and calversion=%s
        '''
        ,(orbit,backend,calversion)
        )
    if status!=1:
        cursor.close()
        return None
    result = cursor.fetchone()
    cursor.close()
    id = result[0]
    return Level1b(id)

class L1bHandler(Level1Handler,PDCKerberosTicket,PDCkftpGetFiles):

    def __init__(self):
        self.ids = []

    @logger
    def makeZPTs(self,force=False):
        db = connect(**connection_str)
        self.matlab_session = GEMMatlab()
        if self.matlab_session.start_matlab():
            for i in self.ids:
                i.m_session = self.matlab_session
                if not i.checkIfValid(db) or force:
                    try:
                        i.makeZPT()
                    except HermodWarning,inst:
                        print stderr,inst
                    except HermodError,inst:
                        print stderr,inst
                    i.addDb(db,attrs=['zpt'])
        self.matlab_session.close_matlab()
        db.close()



    @logger
    def validate(self):
        db = connect(**connection_str)
        for id in ids:
            if not id.validate(db):
                ids.remove(id)

    @logger
    def ticket(self):
        ticket = False
        ticket = self.check()
        if not ticket:
            ticket = self.request()
        return ticket
    
    @logger
    def setnames(self):
        db = connect(**connection_str)
        for id in self.ids:
                id.setname(db)
        db.close()

    @logger
    def make_links(self):
        db = connect(**connection_str)
        for id in self.ids:
                id.link(db)
        db.close()

    @logger
    def download(self,force=False):
        db = connect(**connection_str)
        if self.ticket():
            if self.connect():
                for id in self.ids:
                    if id.l1_OK:
                        id.createdir()
                        hdf = self.get(join(config.get('PDC','PDC_DIR'),id.hdf),join(config.get('GEM','LEVEL1B_DIR'),id.hdf))
                        log = self.get(join(config.get('PDC','PDC_DIR'),id.log),join(config.get('GEM','LEVEL1B_DIR'),id.log))
                        if hdf:
                            id.decompress()
                            id.addDb(db,attrs=['hdf'])
                        if log:
                            id.addDb(db,attrs=['log'])
                self.close()
        db.close()


class Level1b(Level1,MatlabMakeZPT):
    """
    Utility object that operates on a the HDF,LOG and ZPT files related to a row in the level1 table
    """

    @logger
    def __init__(self,id):
        """
        Id number from the level1 table
        """
        self.id = id
        self.l1_OK = False
        self.gzip = True

    @logger
    def decompress(self):
        if self.l1_OK:
            localfile = join(config.get('GEM','LEVEL1B_DIR'),self.hdf)
            if localfile.endswith('.gz'):
                if exists(localfile):
                    retcode =system('/bin/gunzip -fq %s'%(localfile,))
                    if not retcode:
                        self.hdf = self.hdf[:-3]
                else:
                    self.hdf = self.hdf[:-3]
            
    @logger
    def validate(self,opendb):
        cursor = opendb.cursor()
        status = cursor.execute('''select id from level1 where id=%s''',(id,))
        cursor.close()
        return  status==1 

    @logger
    def setname(self,opendb):
        '''Set the names of the files
        '''
        cursor = opendb.cursor()
        cursor.execute('''select filename,logname from level1 where id=%s''',self.id)
        self.hdf,self.log = cursor.fetchone()
        cursor.close()
        self.logfile=stderr
        if  (not self.log is None) or self.log=='':
            self.l1_OK = True
            self.zpt = self.log[:-4]+'.ZPT'
    
    @logger
    def createdir(self): 
        for att in ['hdf','log','zpt']:
            if hasattr(self,att):
                dir = dirname(join(config.get('GEM','LEVEL1B_DIR'),getattr(self,att)))
                if not exists(dir):
                    try:
                        makedirs(dir)
                    except OSError, inst:
                        print >> stderr, inst
                        continue

    @logger
    def link(self,opendb,attrs=['hdf','log','zpt']):
        for attr in attrs:
            if not hasattr(self,attr):
                continue
            #find the name of the mode.
            lprefix='/odin/smr/Data/SMRl1b/V-%i/' 
            prefix= config.get('GEM','LEVEL1B_DIR')
            cursor = opendb.cursor()
            cursor.execute('''
                select distinct a.name,l1.calversion,l1.backend
                from reference_orbit as r
                left join level0_raw as l0
                    on ( floor(start_orbit)<=r.orbit and floor(stop_orbit)>=r.orbit )
                left join level1 as l1
                    on ( r.orbit=l1.orbit)
                join Aero a on (l0.setup=a.mode and l1.backend=a.backend)
                join versions v on (a.id=v.id)
                where l1.id=%s
            ''',(self.id,))
            for i in cursor:
                if i[1]==6 and getattr(self,attr) is not None:
                    #calversion 6 is linked to a deprecated QSMR 
                    #directory format                  
                    if attr=='zpt':
                        #zpt-files are treated differently
                        target =join(lprefix % (i[1],),'ECMWF',i[2],basename(getattr(self,attr)))
                    else:
                        target =join(lprefix%(i[1],),i[0],basename(getattr(self,attr)))
                    source =join(prefix,getattr(self,attr))
                    if not exists(dirname(target)):
                        makedirs(dirname(target))
                    if not exists(target):
                        try:
                            symlink(source,target)
                        except OSError, inst:
                            print >> stderr, inst

 #   def queue(self,queue='new'):
 #       for i in self.launch:
 #           l1copy = dict(self.l1)
 #           l1copy.update(i)
 #           name = 'id%(id)0.2i.%(orbit)0.4X.%(name)s' %(l1copy)
 #           launch =['/usr/bin/qsub','-N%s' %(name),'-lwalltime=%(maxproctime)s,nice=19,nodes=1:hermod:node' % (l1copy),'-q%s' %(queue),'-vORBIT=%(orbit)i,FREQMODE=%(freqmode)i,CALIBRATION=%(calversion)i,FQID=%(fqid)i,NAME=%(name)s,QSMR=%(qsmr)s'%(l1copy),'-e%s%s.err'%(config.get('GEM','logs'),name),'-o%s%s.out'%(config.get('GEM','logs'),name),'/usr/bin/hermodrunjob']
 #           x = subprocess.Popen(launch,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 #           x.stdin.close()
 #           status = x.wait()
 #           if status:
 #               error = "".join(x.stderr.readlines()) + "".join(x.stdout.readlines())
 #               raise HermodError("Could't launch job: %s\n%s" %(name,error))

    @logger
    def addDb(self,opendb,attrs=['hdf','log','zpt'],forcetime=False):
        if self.l1_OK:
            cursor = opendb.cursor()
            for att in attrs:
                if hasattr(self,att):
                    localfile = join(config.get('GEM','LEVEL1B_DIR'),getattr(self,att))
                    if forcetime:
                        try:
                            mtime = float(stat(localfile)[ST_MTIME])
                        except OSError,inst:
                            stderr.write('Couldn''t add file: \n%s\n' %inst)
                            continue
                        date = datetime.fromtimestamp(mtime)
                    else:
                        if not exists(localfile):
                            continue
                        date = datetime.now()
                        
                    #print self.id,getattr(self,att),date
                    cursor.execute('''insert level1b_gem values (%s,%s,%s) on duplicate key update date=%s''',(self.id,getattr(self,att),date,date))
            cursor.close()

def findorbs(dir):
    """Search a directory for level1 files.
    """
    db = connect(**connection_str)
    l1 = L1bHandler()
    pattern = compile('^.*/(.\..)/(.*)/.{2}/O[ABCD]1B(.{4})\.HDF$')
    for root,dirs,files in walk(dir):
        for f in files:
            file = join(root,f)
            m = pattern.match(file)
            if m is not None:
                orbit = int(m.groups()[2],16)
                backend = m.groups()[1]
                calversion = float(m.groups()[0])
                #print m.group(),'%i\t%X\t%s\t%f'%(orbit,orbit,backend,calversion)
                a=fromkeys(orbit,backend,calversion,db)
                if not a is None:
                    l1.ids.append(a)
    db.close()
    l1.setnames()
    return l1

def findids(sqlquery):
    """Find level1-files from a sqlquery.

    Input a sql-query to filter out what ids to use.

    ex. sql='''select id from level1 where orbit<0x0050'''
    Note the returned fields is only id!

    returns a L1bHandler
    """
    db = connect(**connection_str)
    l1 = L1bHandler()
    cursor = db.cursor()
    cursor.execute(*sqlquery)
    for c, in cursor:
        l1.ids.append(Level1b(c))
    cursor.close()
    db.close()
    return l1
        
if __name__=="__main__":
    queryall ="""
    select distinct l1.id
    from level1 l1
    join status s on (l1.id=s.id)
    left join level1b_gem l1bg on (l1.id=l1bg.id)
    where s.status and (l1bg.id is null or l1bg.date<l1.uploaded) 
        and s.errmsg='' and l1.calversion in (6,7,1)
            """
    queryzpt ="""
    SELECT id
    from level1b_gem l1g
    where filename regexp ".*LOG" and not exists (select * from level1b_gem s where s.filename regexp ".*ZPT" and l1g.id=s.id) and l1g.filename regexp "6.*"
            """
    x = findids((queryall ,))
    x.logfile =stderr
    x.setnames()
    x.download()
    x.makeZPTs()
    x.make_links()
    test="""
select distinct l1.id
    from level1 l1
        join orbitmeasurement om on (l1.id=om.l1id)
            join level0_raw l0 on (l0.id=om.l0id)
            join status s on (l1.id=s.id)    
            left join level1b_gem l1bg on (l1bg.id=l1.id)
                where (l1bg.filename regexp '.*HDF' and l1bg.date<l1.uploaded or l1bg.filename is null) and l1.calversion in (1,6,7) and s.status
    """
