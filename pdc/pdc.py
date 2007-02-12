import MySQLdb as sql
import pexpect as p

import os.path as o

from hermod.hermodBase import *

class Fetcher:

    def __init__(self,db):
        self.oklist = []
        self.db = db
        cur = self.db.cursor(sql.Cursors.DictCursor)
        cur.execute('''SELECT distinct id,filename FROM not_downloaded_gem
left join level1 using (id) union SELECT distinct id,logname FROM not_downloaded_gem
left join level1 using (id) order by id''')
        self.download_list = list(cur.fetchall())
        cur.close()
        self.pdcsess = p.spawn('kftp -p esrange.pdc.kth.se')
        status = self.pdcsess.expect('Name.*: ')
        self.pdcsess.write('donal/n')
        self.pdcsess.expect('ftp> ')
        if self.pdcsess.before.find('failed')<>-1:
            self.download()
        else:
            mesg = "Login at PDC-failed, do you have valid kerberos ticket?"
            raise HermodError(mesg)



    def download(self):
        c = self.db.cursor()
        for i in self.download_list:
            pdcfile = "%s%s" % (PDC_DIR,i['filename'])
            gemfile = "%s%s" % (SPOOL_DIR,os.path.basename(i['filename']))
            command = "get %s %s" % (pdcfile,gemfile)
            pdcsess.sendline(command)
            pdcsess.expect('ftp> ')
            if p.before.find('Transfer complete')<>-1:
                if i['filename'].find('HDF')<>-1:
                    c.execute('''insert level1b_gem values (id,type) (%s,%s)''',(i['id'],'HDF'))
                    c.execute('''delete from not_downloaded where id=%s''',(i['id']))
                else:
                    c.execute('''insert level1_gem values (id,type) (%s,%s)''',(i['id'],'LOG'))
        self.pdcsess.sendline('bye')
            
                
                
    def getFiles(self,row):
        log = "%s/%s" % (PDC_DIR,row['logname'])
        hdf = "%s/%s" % (PDC_DIR,row['filename'])
        destlog "%s/%s" % (SPOOL_DIR,o.basename(row['logname']))
        desthdf "%s/%s" % (SPOOL_DIR,o.basename(row['filename']))
        
                        







