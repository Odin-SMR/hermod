#!/usr/bin/python2.5

'''
This script runs on a computing node, it starts Matlab and parses its output.

'''

from sys import stderr, stdout, argv, exit
from os import getenv,remove,environ
from os.path import join,exists
from string import Template
from datetime import datetime
from re import compile 

from MySQLdb import connect
from MySQLdb.cursors import DictCursor

from pyhdf.HDF import HDF, HDF4Error
from pyhdf import VS


from odin.hermod.session import GEMMatlab
from odin.hermod.pdc import PDCKerberosTicket,PDCkftpGetFiles
from odin.hermod.hermodBase import connection_str,HermodError,HermodWarning,config


class ILevel2FileNames:
    pass

class GEMLevel2FileNames(ILevel2FileNames):
    

    def setname(self):
        prefix={'AC1':'B','AC2':'C'}
        db = connect(**connection_str)
        cursor = db.cursor(DictCursor)
        #get all other names and parameters needed
        status = cursor.execute('''
            select mid as
                midfreq
            from Aero 
            where id=%(fqid)s 
            group by id''',
            (self.parameters))
        if status==1:
            self.parameters.update(cursor.fetchone())
        else:
            print "midfreq %i"%status
        cursor.close()
        db.close()
        self.parameters['prefix']='SCH_%(midfreq)i_' %self.parameters + '%s' % prefix[self.parameters['backend']]
        self.parameters['suffix']="_%.3i"%int(self.parameters['qsmr'].replace('-',''))
        self.parameters['l2file'] = join('SMRhdf','Qsmr-%(qsmr)s','%(name)s','%(prefix)s%(orbit).4X%(suffix)s.L2P') %self.parameters
        self.parameters['auxfile'] = join('SMRhdf','Qsmr-%(qsmr)s','%(name)s','%(prefix)s%(orbit).4X%(suffix)s.AUX') %self.parameters
        self.parameters['pdcl2file'] = join('version_%s'%self.parameters['qsmr'].replace('-','.'),'%(name)s','%(prefix)s%(orbit).4X%(suffix)s.L2P') %self.parameters


class GEMRunner(GEMLevel2FileNames,PDCkftpGetFiles,PDCKerberosTicket):
    
    def __init__(self, kwargs):
        param = dict()
        param['id'] = int(kwargs['id'])
        param['fqid'] = int(kwargs['fqid'])
        param['qsmr'] = kwargs['version']
        param['orbit']= int(kwargs['orbit'])
        param['backend']= kwargs['backend']
        param['calversion']= float(kwargs['calversion'])
        param['name']= kwargs['name']
        param['process_time']= kwargs['process_time']
        workdir = getenv('TMPDIR')
        if workdir is None:
            a =getenv('PBS_JOBID')
            if not a is None:
                workdir = join('/tmp', 'tmp'+a.split('.')[0])
            else:
                workdir = '/tmp'
        param['dir'] = workdir
        self.parameters = param

    def delete_old(self):
        basefile = join(config.get('GEM','SMRL2_DIR'),self.parameters['l2file'][:-3])
        for attr in ['L2P','ERR','AUX']:
            if exists(basefile+'.'+attr):
                remove(basefile+'.'+attr)
        db = connect(**connection_str)
        c = db.cursor()
        c.execute('''
                delete from level2files 
                where id=%(id)s and version=%(qsmr)s 
                    and fqid=%(fqid)s
                    ''',
                self.parameters)
        c.execute('''
                delete from level2 
                where id=%(id)s and version2=%(qsmr)s 
                and fqid=%(fqid)s
                ''',
                self.parameters)
        c.close()
        db.close()


    def readData(self):
        """
        Reads a the associated hdf file. Returns a list of dictionaries. If an error occurs it returns an empty list.
        """
        table = "Geolocation"
        file = join(config.get('GEM','SMRL2_DIR'),self.parameters['l2file'])
        try:
            f = HDF(file)                # open 'inventory.hdf' in read mode
            vs = f.vstart()                 # init vdata interface
            vd = vs.attach(table)   # attach 'INVENTORY' in read mode
            index = vd.inquire()[2]
            info = []
            if hasattr(self,'aux'):
                a = iter(self.aux)
            else:
                a = [dict() for i in range(200)]
            for i in vd[:]:
                try:
                    data = a.next()
                    data.update(dict(zip(index,i)))
                except StopIteration:
                    pass
                m = int(data.pop('Ticks')*1000000)
                if m>999999:
                    m=999999
                data['date']= datetime(data.pop('Year'),data.pop('Month'),data.pop('Day'),data.pop('Hour'),data.pop('Min'),data.pop('Secs'),m)
                data.update(self.parameters)
                info.append(data)
                
            self.geolocation = info
            vd.detach()               # "close" the vdata
            vs.end()                  # terminate the vdata interface
            f.close()                 # close the HDF file
        except HDF4Error,inst:
            mesg = "error reading %s: %s" % (file,inst)
            raise HermodError(mesg)
        self.parameters['pscans']=len(self.geolocation)

    def addData(self):
        """
        Adds data into the odin database
        """
        db = connect(**connection_str)
        c = db.cursor()
        c.execute('''INSERT level2files (id,fqid,version,nscans,verstr,hdfname,pdcname,processed) values (%(id)s,%(fqid)s,%(qsmr)s,%(pscans)s,%(verstr)s,%(l2file)s,%(pdcl2file)s,now())''',(self.parameters))
	for i in self.geolocation:
	   test = c.execute ("""INSERT level2 (id,version2,latitude,longitude,mjd,date,sunZD,fqid,quality,p_offs,f_shift,chi2,chi2_y,chi2_x,marq_start,marq_stop,marq_min,n_iter,scanno) values (%(id)s,%(qsmr)s,%(Latitude)s,%(Longitude)s,%(MJD)s,%(date)s,%(SunZD)s,%(fqid)s,%(Quality)s,%(P_Offs)s,%(F_Shift)s,%(Chi2)s,%(Chi2_y)s,%(Chi2_x)s,%(Marq_Start)s,%(Marq_Stop)s,%(Marq_Min)s,%(N_Iter)s,%(ScanNo)s)""", i)
        c.close()
        db.close()
    
    def readAuxFile(self):
        data=[]
        typelist = [int,float,float,str,int,float,int,float,float,float,float,float,float,float,float,int]
        #print "reading auxfile: %s" % self.auxfile
        filename = join(config.get('GEM','SMRL2_DIR'),self.parameters['auxfile'])
        try:
            f = open(filename)
        except:
            raise HermodError('No auxfile found %s'%(filename))
        try:
            versionnr = False
            headers = False
            if f.readline()[0] == '#':
                headers = True
            if f.readline()[0] == '#':
                versionnr = True
            f.seek(0)
            if versionnr:
                ver = f.readline().strip().split(' ')[1]
            else:
                ver = None
            if headers:
                head = f.readline()
                header = head.split()[1:]
            for line in f:
                    fields = line.split()
                    converted = [g(h) for g,h in zip(typelist,fields)]
                    map = dict(zip(header,converted))
                    map['ver'] = ver
                    data.append(map) 
        finally:
            f.close()
            self.parameters['verstr'] = ver
            self.aux = data

    def upload(self):
        db = connect(**connection_str)
        cur = db.cursor()
        if not self.renew():
            self.destroy()
            self.request()
        if self.connect():
            if self.put(join(config.get('GEM','SMRL2_DIR'),self.parameters['l2file']),
                    join(config.get('PDC','smrl2_dir'),self.parameters['pdcl2file'])):
                cur.execute('''update level2files set uploaded=now() where id=%(id)s and fqid=%(fqid)s and version=%(qsmr)s''',self.parameters)
        self.close()
        cur.close()
        db.close()

def main():
    errors = False
    errmsg = ""
    for i in ['id','version','fqid','orbit','backend','process_time','calversion']:
        if not environ.has_key(i):
            raise HermodError('missing evironment variable "%s"' %i )
    run = GEMRunner(environ)
    run.setname()
    run.delete_old()
    commands = [
            "set(gcf,'Visible','off')",
            "qsmr_startup",
            "qsmr_inv_op('%(name)s','%(orbit)0.4X','%(orbit)0.4X','%(dir)s')"
                % run.parameters,
            ]
    msession = GEMMatlab()
    msession.start_matlab()
    for c in commands:
        try: 
            result = msession.matlab_command(c)
        except RuntimeError,msg:
            errors=True
            errmsg = errmsg + str(msg)
            print >> stderr,msg
            break
    msession.close_matlab()
    if not errors:
        try:
            run.readAuxFile()
            run.readData()
            run.addData()
            run.upload()
        except HermodError,inst:
            msg = str(inst)
            errmsg = errmsg +msg
            print >> stderr,msg
    db = connect(**connection_str)
    cur = db.cursor()
    run.parameters['errmsg']= errmsg
    cur.execute('''insert statusl2 (id,fqid,version,errmsg) 
        values (%(id)s,%(fqid)s,%(qsmr)s,%(errmsg)s)
        on duplicate key update proccount=proccount+1,
            errmsg=%(errmsg)s,date=now()
        ''',run.parameters)
    cur.close()
    db.close()
    
if __name__=='__main__':
    main()
