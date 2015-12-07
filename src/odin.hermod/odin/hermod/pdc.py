import MySQLdb as sql
import os
import os.path as o
import sys
import subprocess

from odin.config.environment import config

from interfaces import IKerberosTicket,IGetFiles
from pexpect import spawn,EOF,TIMEOUT
from subprocess import Popen,PIPE
from sys import stderr
from gemlogger import logger


class PDCKerberosTicket(IKerberosTicket):

    def request(self):
        conf = config()
        ticket = spawn(
            '/usr/bin/kinit -f -r 154h -l 26h  %s@%s'%(
                conf.get('PDC','user'),conf.get('PDC','principal')))
        ticket.expect('.*Password: $')
        ticket.sendline(conf.get('PDC','passwd'))
        ticket.expect(EOF)
        ticket.close()
        retcode = ticket.exitstatus
        return retcode==0

    def check(self):
        getticket = Popen(['/usr/bin/klist','-t'],stdout=PIPE,stderr=PIPE)
        retcode = getticket.wait()
        msg = getticket.stdout.read()
        getticket.stdout.close()
        return (not retcode)

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
        conf = config()
        self.counter = 0
        self.session = spawn(
            '/usr/bin/kftp',['-p',conf.get('PDC','host')],timeout=30)
        self.pattern = self.session.compile_pattern_list([
            '.*complete.*ftp> $',
            '.*Timeout.*ftp> $',
            '.*No such file.*ftp> $',
            '.*ftp> $',
            EOF,
            TIMEOUT,
            ])
        index = self.session.expect(['Name.*: ', EOF, TIMEOUT])
        if index != 0:
            # print "Connect fail with index: {0}".format(index)
            return False
        else:
            self.session.sendline('%s' % conf.get('PDC', 'user'))

        index = self.session.expect(self.pattern, timeout=20)
        # print "Connect will return with index: {0}".format(index)
        return index == 3

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
