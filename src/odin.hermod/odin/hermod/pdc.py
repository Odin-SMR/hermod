import MySQLdb as sql
import pexpect as p
import os
import os.path as o
import sys
import subprocess

from odin.hermod.hermodBase import *

from interfaces import IKerberosTicket,IGetFiles
from pexpect import spawn,EOF,TIMEOUT
from subprocess import Popen,PIPE
from sys import stderr
from gemlogger import logger

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
            ticket = p.spawn('kinit -f --afslog --renewable -l 1h %s@%s'%(config.get('PDC','user'),config.get('PDC','principal')))
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
        pdcsess.expect('ftp> ')
        if pdcsess.before.find('fail')==-1:
            for pair in srcDestPair:
                pdcsess.sendline('put %s %s'%pair)
                index = pdcsess.expect(['Transfer complete.','Permission denied','No such file or directory','Is a directory',p.EOF,p.TIMEOUT],timeout=7)
                if index == 0:
                    pass
                elif index == 1:
                    print "Permission error"
                elif index == 2:
                    raise HermodError("No such file")
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
                    pass
                elif index == 1:
                    print "Permission error"
                elif index == 2:
                    raise HermodError("No such file: %s" %(pair[0]))
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

class PDCKerberosTicket(IKerberosTicket):

    @logger
    def request(self):
        ticket = spawn('kinit -f -r 7d -l 30d  %s@%s'%(config.get('PDC','user'),config.get('PDC','principal')))
        ticket.expect('.*Password: $')
        ticket.sendline(config.get('PDC','passwd'))
        ticket.expect(EOF)
        ticket.close()
        retcode = ticket.exitstatus
        return retcode==0

    @logger
    def check(self):
        getticket = Popen(['/usr/bin/klist'],stdout=PIPE,stderr=PIPE)
        retcode = getticket.wait()
        msg = getticket.stdout.read()
        getticket.stdout.close()
        return (not retcode and msg.find(config.get('PDC','principal'))>=0)

    @logger
    def renew(self):
        getticket = Popen(['/usr/bin/kinit','-R'],stderr=PIPE)
        retcode = getticket.wait()
        msg = getticket.stderr.read()
        getticket.stderr.close()
        return retcode==0

    def destroy(self):
        destroy = Popen(['/usr/bin/kdestroy'],stderr=PIPE)
        retcode = destroy.wait()
        destroy.stderr.close()
        return True

class PDCkftpGetFiles(IGetFiles):

    @logger
    def count(self):
        if self.counter> 400:
            self.close()
            self.connect()
        else:
            self.counter = self.counter + 1

    @logger
    def connect(self):
        self.counter = 0
        self.session = spawn('/usr/bin/kftp',['-p','pisces.pdc.kth.se'],timeout=30)
        self.pattern = self.session.compile_pattern_list([
            '.*complete.*ftp> $',
            '.*Timeout.*ftp> $',
            '.*No such file.*ftp> $',
            '.*ftp> $',
            EOF,
            TIMEOUT,
            ])
        index=self.session.expect(['.*ftp> $',EOF,TIMEOUT])
        self.session.sendline('user %s'%config.get('PDC','user'))
        index=self.session.expect(['.*ftp> $',EOF,TIMEOUT])
        return True

    @logger
    def close(self):
        self.session.sendline('bye')
        self.session.expect(['.*Goodbye.$',EOF,TIMEOUT],timeout=5)
        self.session.close()
        return True

    @logger
    def put(self,src,dest):
        index = -1
        if self.session.isalive():
            self.session.sendline('put %s %s'%(src,dest))
            index = self.session.expect(self.pattern,timeout=20)
        self.count()
        return index==0

    @logger
    def get(self,src,dest):
        index = -1
        if self.session.isalive():
            self.session.sendline('get %s %s'%(src,dest))
            index = self.session.expect(self.pattern,timeout=20)
        self.count()
        return index==0

    def delete(self,src):
        index = -1
        if self.session.isalive():
            self.session.sendline('delete %s'%(src,))
            index = self.session.expect(self.pattern,timeout=5)
        self.count()
        return index==3

if __name__ == "__main__":
    ticket = PDCKerberosTicket()
    if not ticket.check():
        if not ticket.request():
            raise Exception, "No ticket available"
    ftp = PDCkftpGetFiles()
    if ftp.connect():
        if ftp.put('testlocal.txt','test.txt'):
            if ftp.get('test.txt','testremote.txt'):
                pass
        ftp.close()
    else:
        raise Exception, "No ftpconnection available"
        


