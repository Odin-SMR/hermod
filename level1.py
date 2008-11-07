from MySQLdb import connect
from MySQLdb.cursors import DictCursor
from os import makedirs,walk
from os.path import join,basename,dirname,splitext,exists
from hermod.hermodBase import config,connection_str,HermodError
from subprocess import Popen,PIPE
from pexpect import spawn,EOF
from re import compile
from os import stat,system
from stat import ST_MTIME
from datetime import datetime
from sys import stderr
from pdc import PDCkftpGetFiles,PDCKerberosTicket

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
    return Level1(id)

class L1bHandler(PDCKerberosTicket,PDCkftpGetFiles):

    def __init__(self):
        self.ids = []

    def validate(self):
        db = connect(**connection_str)
        for id in ids:
            if not id.validate(db):
                ids.remove(id)

    def ticket(self):
        ticket = False
        ticket = self.check()
        if not ticket:
            ticket = self.request()
        return ticket
    
    def setnames(self):
        db = connect(**connection_str)
        cursor = db.cursor()
        for i in self.ids:
            status = cursor.execute("""
                select filename,logname
                from level1
                where id = %s
                """
                ,(i())
                )
            if status==1:
                i.setname(cursor.fetchall()[0])
        cursor.close()
        db.close()

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


class Level1:
    """
    Utility object that operates on a the HDF,LOG and ZPT files related to a row in the level1 table
    """

    def __init__(self,id):
        """
        Id number from the level1 table
        """
        self.id = id
        self.l1_OK = False
        self.gzip = True

    def __call__(self):
        return self.id

    def __repr__(self):
        return str(self.id)


    def download(self):
        """
        set the download marker
        """
        self.download=True

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
            
    def validate(self,opendb):
        cursor = opendb.cursor()
        status = cursor.execute('''select id from level1 where id=%s''',(id,))
        cursor.close()
        return  status==1 

    def setname(self,filetuple):
        '''filtuple is (databasefilename,databaselogname)'''
        self.hdf,self.log = filetuple
        if not (self.hdf is None) or (not self.log is None) or self.hdf=='' or self.log=='':
            self.l1_OK = True
            self.zpt = self.log[:-4]+'.ZPT'
    
    def createdir(self):
        for att in ['hdf','log','zpt']:
            if hasattr(self,att):
                dir = dirname(join(config.get('GEM','LEVEL1B_DIR'),getattr(self,att)))
                try:
                    makedirs(dir)
                except OSError, inst:
                    continue

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
        l1.ids.append(Level1(c))
    cursor.close()
    db.close()
    return l1
        
if __name__=="__main__":
    x = L1bHandler()
    x.ids=[Level1(67),Level1(32)]
    x.setnames()
    x.download()
