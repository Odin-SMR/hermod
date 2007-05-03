import MySQLdb as sql
import pexpect as p
import os
import os.path as o
import sys
import subprocess

from hermod.hermodBase import *

class Fetcher:
    """
    Fetcher reads smr.not_downloaded_gem table and downloads all files to SPOOL_DIR
    """

    def __init__(self,db):
        self.db = db
        cur = self.db.cursor(sql.cursors.DictCursor)
        cur.execute('''SELECT distinct id,filename FROM not_downloaded_gem natural join level1 natural join status where status union SELECT distinct id,logname FROM not_downloaded_gem natural join level1 natural join status where status order by id''')
        self.download_list = list(cur.fetchall())
        cur.close()
        command0 = 'kftp -p %s' % config.get('PDC','host')
        self.pdcsess = p.spawn(command0,timeout=300)
        status = self.pdcsess.expect('Name.*')
        self.pdcsess.sendline(config.get('PDC','user'))
        self.pdcsess.expect('ftp> ')
        if self.pdcsess.before.find('fail')==-1:
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
            self.pdcsess.sendline(command)
            self.pdcsess.expect('ftp> ')
            if self.pdcsess.before.find('Transfer complete')<>-1:
                if i['filename'].find('HDF')<>-1:
                    command2 = 'gunzip -q -f %s' % (gemfile)
                    status = os.system(command2)
                    if status == 0:
                        c.execute('''insert level1b_gem (id,filename) values (%s,%s)
                                on duplicate key update date=now()''',(i['id'],o.splitext(i['filename'])[0]))
                        c.execute('''delete from not_downloaded_gem where id=%s''',(i['id']))
                        #create zptfile?
                        #launch job?
                    else:
                        #what to do if the file  contained an error?
                        print >> sys.stderr, "Problems while gunzipping file:",i['filename']
                else:
                    c.execute('''insert level1b_gem (id,filename) values (%s,%s)
                            on duplicate key update date=now()''',(i['id'],i['filename']))
            else:
                print >> sys.stderr, "Could not download this PDC-file: %s " % pdcfile
                # in future insert a failure messeage into smr.status
        self.pdcsess.sendline('bye')
            
                
                
class connection:
    def __init__(self):
        session = subprocess.Popen(['klist','-s']) 
        session_st = session.wait()

        if session_st:
            #create any existing ticket
            dest = subprocess.Popen(['kdestroy'])
            dest_st = dest.wait()
            if dest_st:
                raise HermodError('Could not destroy tickets')

            #create a new ticket
            ticket = p.spawn('kinit -f --afslog --renewable -l 10m %s@%s'%(config.get('PDC','user'),config.get('PDC','principal')))
            ticket.expect('Password:')
            ticket.sendline(config.get('PDC','passwd'))
            ticket.expect(p.EOF)
            ticket.close()
            if ticket.exitstatus:
                raise HermodError("Could not get a ticket from %s" %(config.get('PDC','principal')))
#        else:
#            renew = subprocess.Popen(['kinit','-R','--afslog','--renewable','-l 1h'])
#            renew_st = renew.wait()
#            if renew_st:
#                raise HermodError("Could not renew the ticket from %s" %(config.get('PDC','principal')))
#
    def uploads(self,srcDestPair):
        pdcsess = p.spawn('kftp -p %s' %(config.get('PDC','host')) ,timeout=300)
        status = pdcsess.expect('Name.*')
        pdcsess.sendline(config.get('PDC','user'))
        pdcsess.expect('ftp> ')
        if pdcsess.before.find('fail')==-1:
            for pair in srcDestPair:
                pdcsess.sendline('put %s %s'%pair)
                index = pdcsess.expect(['Transfer complete.','Permission denied','No such file or directory','Is a directory',p.EOF,p.TIMEOUT],timeout=7)
                if index == 0:
                    print "OK"
                elif index == 1:
                    print "Permission error"
                elif index == 2:
                    print "No such file"
                elif index == 3:
                    print "target is a directory"
                elif index == 4:
                    print "EOF"
                elif index == 5:
                    print 'before\n',pdcsess.before,'after\n',pdcsess.after
            pdcsess.sendline('bye')
            pdcsess.expect(p.EOF)
            pdcsess.close()
        else:
            raise HermodError("Login at PDC failed, %s@%s" %(config.get('PDC','user'),config.get('PDC','host')))

    def downloads(self,srcDestPair):
        pdcsess = p.spawn('kftp -p %s' %(config.get('PDC','host')) ,timeout=300)
        status = pdcsess.expect('Name.*')
        pdcsess.sendline(config.get('PDC','user'))
        pdcsess.expect('ftp> ')
        if pdcsess.before.find('fail')==-1:
            for pair in srcDestPair:
                pdcsess.sendline('get %s %s'%pair)
                index = pdcsess.expect(['Transfer complete.','Permission denied','No such file or directory','Is a directory',p.EOF,p.TIMEOUT],timeout=7)
                if index == 0:
                    print "OK"
                elif index == 1:
                    print "Permission error"
                elif index == 2:
                    print "No such file"
                elif index == 3:
                    print "target is a directory"
                elif index == 4:
                    print "EOF"
                elif index == 5:
                    print 'before\n',pdcsess.before,'after\n',pdcsess.after
            pdcsess.sendline('bye')
            pdcsess.expect(p.EOF)
            pdcsess.close()
        else:
            raise HermodError("Login at PDC failed, %s@%s" %(config.get('PDC','user'),config.get('PDC','host')))

   
        


    



def test():
    db = sql.connect(host=config.get('WRITE_SQL','host'), user=config.get('WRITE_SQL','user'), passwd=config.get('WRITE_SQL','passwd'), db='smr')
    a = Fetcher(db)
    db.close()


if __name__ == "__main__":
    pass
    #test()
    a = connection()
    print "uploads"
    a.uploads([('/home/joakim/work/test.txt','test.txt'),('/home/joakim/work/test.txt','test2.txt')])
    print "downloads"
    a.downloads([('test.txt','test_down.txt')])







