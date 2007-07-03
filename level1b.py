
#!/usr/bin/python

"""
level1 downloads files from pdc and launches them into the cluster.
"""

import MySQLdb
import os.path
from hermod.hermodBase import *
from hermod.pdc import connection
from hermod.ecmwf import ZPTfile
import subprocess

def level1Factory(level1tuple,db):
    cal = level1tuple['calversion']
    if cal==6:
        return l1b_v6(level1tuple,db)
    elif cal==7:
        return None
        #return l1b_v7(level1tuple,db)
    else:
        return None


class l1b:
    '''
    Find files not yet downloaded, prepare all auxilary files and launch into the cluster
    '''
    def __init__(self,l1tuple,db):
        '''
        A l1tuple contains every field in level1 and status table:
        id, orbit, backend, freqmode, nscans, nspectra, calversion, attversion,
        processed, uploaded, filename, logname, start_utc, stop_utc, sucess,
        errmesg
        '''
        self.l1 = dict(l1tuple)
        self.l1['freqmode'] = [int(i) for i in self.l1['freqmode'].split(',')]
        self.l1['freqmode'].append(199)
        self.l1['calibration'] = int(self.l1['calversion'])
        self.db = db
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''select * from odin.Versions natural join odin.Freqmodes 
                where freqmode in %(freqmode)s and active and calibration=%(calibration)s''',
                (self.l1))
        self.l1['freqmode'].remove(199)
        self.launch = [ dict(i) for i in cursor]
        cursor.close()

    def download(self):
        pdc = connection()
        try:
            pdc.downloads(
                    [
                        (
                            os.path.join(config.get('PDC','PDC_DIR'),self.l1['filename']),
                            os.path.join(config.get('GEM','LEVEL1B_DIR'),self.l1['filename'])
                            ),
                        (
                            os.path.join(config.get('PDC','PDC_DIR'),self.l1['logname']),
                            os.path.join(config.get('GEM','LEVEL1B_DIR'),self.l1['logname'])
                            )
                        ]
                    )
        except HermodError, inst:
            raise HermodError("Couln't fetch files from PDC: %s" %(inst))

    def filesystem(self):
        retcode = subprocess.call(['/bin/gunzip','-f',os.path.join(config.get('GEM','LEVEL1B_DIR'),self.l1['filename'])])
        if not retcode:
            self.l1['filename'] = os.path.splitext(self.l1['filename'])[0]
        else:
            raise HermodError("Couldn't decompress HDF file: %s" %(os.path.join(config.get('GEM','LEVEL1B_DIR'),self.l1['filename'])))

    def database(self):
            cursor = self.db.cursor()
            status = cursor.execute('''delete from level1b_gem where id=%(id)s''',(self.l1))
            status=cursor.execute('''insert level1b_gem (id,filename) values (%(id)s,%(filename)s)''',(self.l1))
            status = cursor.execute('''insert level1b_gem (id,filename) values (%(id)s,%(logname)s)''',(self.l1))
            cursor.execute('''delete from not_downloaded_gem where id=%(id)s''',(self.l1))

    def createAux(self):
        x = ZPTfile(self.db)
        x.getNonExisting()
        x.genZPTs()

    def linkandmove(self):
        pass

    def queue(self,queue='new'):
        for i in self.launch:
            l1copy = dict(self.l1)
            l1copy.update(i)
            name = 'id%(id)0.2i.%(orbit)0.4X.%(name)s' %(l1copy)
            launch =['/usr/bin/qsub','-N%s' %(name),'-lwalltime=%(maxproctime)s,nice=19' % (l1copy),'-q%s' %(queue),'-vORBIT=%(orbit)i,FREQMODE=%(freqmode)i,CALIBRATION=%(calversion)i,FQID=%(fqid)i,NAME=%(name)s,QSMR=%(qsmr)s'%(l1copy),'-e%s%s.err'%(config.get('GEM','logs'),name),'-o%s%s.out'%(config.get('GEM','logs'),name),'/usr/bin/hermodrunjob']
            x = subprocess.Popen(launch,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            x.stdin.close()
            status = x.wait()
            if status:
                error = "".join(x.stderr.readlines()) + "".join(x.stdout.readlines())
                raise HermodError("Could't launch job: %s\n%s" %(name,error))

class l1b_v7(l1b):
    pass

class l1b_v6(l1b):
    def linkandmove(self):
        for i in self.launch:
            l1copy = dict(self.l1)
            l1copy.update(i)
            file = os.path.join(config.get('GEM','LEVEL1B_DIR'),l1copy['filename'])
            log = os.path.join(config.get('GEM','LEVEL1B_DIR'),l1copy['logname'])
            dir = os.path.join(config.get('GEM','SMRL1B_DIR'),'V-%(calibration)i','%(name)s') %(l1copy)
            zpt = os.path.join(config.get('GEM','SMRL1B_DIR'),'V-%(calibration)i','ECMWF','%(backend)s') %(l1copy)
            x = subprocess.Popen(['/bin/mkdir','-p',dir],stderr=subprocess.PIPE,stdout=subprocess.PIPE)
            status = x.wait()
            x = subprocess.Popen(['/bin/ln','-s','-t%s'%(dir),file,log],stderr=subprocess.PIPE,stdout=subprocess.PIPE)
            status = x.wait()
            x = subprocess.Popen(['/bin/ln','-s','-t%s'%(zpt),file.replace('HDF','ZPT')],stderr=subprocess.PIPE,stdout=subprocess.PIPE)
            status = x.wait()



if __name__=="__main__":
    db = MySQLdb.connect(host=config.get('WRITE_SQL','host'), user=config.get('WRITE_SQL','user'), passwd=config.get('WRITE_SQL','passwd'), db='smr')
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    status = cursor.execute('''SELECT distinct * FROM test  natural join level1 natural join status''')
    level1objects = [level1Factory(i,db) for i in cursor]
    cursor.close()
    db.close()
    for i in level1objects:
        if i is not None:
            i.download()
            i.filesystem()
            i.database()
            i.createAux()
            i.linkandmove()
            i.queue()


