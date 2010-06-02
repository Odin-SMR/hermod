import MySQLdb as sql
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


class PDCKerberosTicket(IKerberosTicket):

    def request(self):
        ticket = spawn('kinit -f -r 7d -l 30d  %s@%s'%(config.get('PDC','user'),config.get('PDC','principal')))
        ticket.expect('.*Password: $')
        ticket.sendline(config.get('PDC','passwd'))
        ticket.expect(EOF)
        ticket.close()
        retcode = ticket.exitstatus
        return retcode==0

    def check(self):
        getticket = Popen(['/usr/bin/klist'],stdout=PIPE,stderr=PIPE)
        retcode = getticket.wait()
        msg = getticket.stdout.read()
        getticket.stdout.close()
        return (not retcode and msg.find(config.get('PDC','principal'))>=0)

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

    def count(self):
        if self.counter> 400:
            self.close()
            self.connect()
        else:
            self.counter = self.counter + 1

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

    def close(self):
        self.session.sendline('bye')
        self.session.expect(['.*Goodbye.$',EOF,TIMEOUT],timeout=5)
        self.session.close()
        return True

    def put(self,src,dest):
        index = -1
        if self.session.isalive():
            self.session.sendline('put %s %s'%(src,dest))
            index = self.session.expect(self.pattern,timeout=20)
        self.count()
        return index==0

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
