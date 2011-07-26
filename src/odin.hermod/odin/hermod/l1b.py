from odin.config.database import connect
from odin.hermod.pdc import PDCKerberosTicket,PDCkftpGetFiles
from odin.config.environment import config,set_hermod_logging
from os import mkdir,system
from os.path import dirname,join,isdir,split
import logging

class L1bDownloader(PDCKerberosTicket,PDCkftpGetFiles):
    
    def __init__(self,lists):
        self.lists = lists
        self.config = config()
        self.db = connect()
        self.cursor = self.db.cursor()
        self.log = logging.getLogger('__name__')

    def gettickets(self):
        if not self.renew():
            self.destroy()
            self.request()
            self.log.debug('Accquired a new kerberos ticket from PDC')
        else:
            self.log.debug('Using an old ticket')
    
    def download(self):
        self.connect()
        self.log.debug('Connected to PDC via ftp')
        for f in self.lists:
            if f[1]=='' or f[1] is None:
                self.log.warn("HDF file entry is empty, database id {0}".format(
                        f[0]))
            if f[2] == '' or f[2] is None:
                self.log.warn("LOG file entry is empty, database id {0}".format(
                        f[0]))
            else:
                for num,typ in enumerate(['HDF','LOG']):
                    remote = join(
                            self.config.get('PDC','PDC_DIR'),
                            f[num+1],
                            )
                    local = join(
                            self.config.get("GEM","LEVEL1B_DIR"),
                            f[num+1],
                            )
                    makedir(dirname(local))
                    self.get(remote,local)
                    self.log.info('Downloaded {}'.format(local)) 
                    if typ=='HDF':
                        retcode =system('/bin/gunzip -fq %s'%(local,))
                        if retcode!=0:
                            continue
                        self.log.info('Unzipped {}'.format(f[1])) 
                        self.register(f[0],f[num+1][:-3])
                    else:
                        self.register(f[0],f[num+1])
        self.close()

    def register(self, idn, name):
        self.cursor.execute("""
                replace level1b_gem
                values (%s,%s,CURRENT_TIMESTAMP)
                """,(idn,name))
        self.log.debug('Regisetered in data base, using sql: {0}'.format(
                self.cursor._last_executed))

    def finish(self):
        self.cursor.close()
        self.db.close()
        self.log.debug('Exiting')


def makedir(dirname):
    '''Makes the directories to ensure the path to filename exists.
    '''
    if not isdir(dirname):
        makedir(split(dirname)[0])
        mkdir(dirname)
    else:
        return



def downloadl1bfiles():
    set_hermod_logging()
    log = logging.getLogger(__name__)
    log.info('Scanning database for new level1 files')
    db = connect()
    cursor = db.cursor()
    status = cursor.execute('''
            select distinct l1.id,l1.filename,l1.logname
            from level1 l1
            join status s on (l1.id=s.id)
            left join level1b_gem l1bg on (l1.id=l1bg.id)
            where s.status and (l1bg.id is null or l1bg.date<l1.uploaded) 
                and s.errmsg='' and l1.calversion in (6,7);
            ''')
    log.info('Found {} new HDF-files'.format(status))
    result = cursor.fetchall()
    log.debug('Issued the query: {}'.format(cursor._last_executed))
    cursor.close()
    db.close()
    l1b = L1bDownloader(result)
    l1b.gettickets()
    l1b.download()
    l1b.finish()

