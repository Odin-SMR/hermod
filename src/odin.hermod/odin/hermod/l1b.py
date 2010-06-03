from odin.config.database import connect
from odin.hermod.pdc import PDCKerberosTicket,PDCkftpGetFiles
from odin.config.environment import config
from os import mkdir,system
from os.path import dirname,join,isdir,split

class L1bDownloader(PDCKerberosTicket,PDCkftpGetFiles):
    
    def __init__(self,lists):
        self.lists = lists
        self.config = config()
        self.db = connect()
        self.cursor = self.db.cursor()

    def gettickets(self):
        if not self.check():
            self.request()
        else:
            self.renew()
    
    def download(self):
        self.connect()
        for f in self.lists:
            print f
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
                if typ=='HDF':
                    retcode =system('/bin/gunzip -fq %s'%(local,))
                    if retcode!=0:
                        continue
                    self.register(f[0],f[num+1][:-3])
                else:
                    self.register(f[0],f[num+1])
        self.close()

    def register(self, idn, name):
        self.cursor.execute("""
                replace level1b_gem
                (id,filename)
                values (%s,%s)
                """,(idn,name))

    def finish(self):
        self.cursor.close()
        self.db.close()


def makedir(dirname):
    '''Makes the directories to ensure the path to filename exists.
    '''
    if not isdir(dirname):
        makedir(split(dirname)[0])
        mkdir(dirname)
    else:
        return



def downloadl1bfiles():
    db = connect()
    cursor = db.cursor()
    cursor.execute('''
            select l1.id,l1.filename,l1.logname
            from level1 l1
            join status s on (l1.id=s.id)
            left join level1b_gem l1bg on (l1.id=l1bg.id)
            where s.status and (l1bg.id is null or l1bg.date<l1.uploaded) 
                and s.errmsg='' and l1.calversion in (6,7);
            ''')
    result = cursor.fetchall()
    cursor.close()
    db.close()
    l1b = L1bDownloader(result)
    l1b.gettickets()
    l1b.download()
    l1b.finish()

if __name__=="__main__":
    downloadl1bfiles()
