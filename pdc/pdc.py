import MySQLdb as sql
import pexpect as p


from hermod.hermodBase import *

class Fetcher:

    def __init__(self,db):
        self.db = db



        cur = self.db.cursor(sql.Cursors.DictCursor)
        cur.execute('''select distinct id,filename,logname from not_downloaded_gem natural join level1''')
        self.download_list = list(cur.fetchall())
        cur.close()
        self.pdcsess = p.spawn('kftp -p esrange.pdc.kth.se')
        self.pdcsess.expect('Name.*: ')
        self.pdcsess.write('donal/n')
        
        self.download()



    def download(self):
        if self.validTicket():
            for i in self.download_list:
                self.getFile(i)
                if self.verify(i):
                    self.accept(i)
        else
            mesg = "No valid ticket for PDC"
            raise HermodError(mesg)

    def getFiles(self,row):
        log = "%s/%s" % (PDC_DIR,row[logname])
        hdf = "%s/%s" % (PDC_DIR,row[filename])
        dest "%s/%s" % (SPOOL_DIR)







