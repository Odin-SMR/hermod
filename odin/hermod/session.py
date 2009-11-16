import os,subprocess,fcntl,sys,os.path,tempfile,MySQLdb
from hermod.level2 import *
from odin.hermod.hermodBase import *
from pexpect import spawn,EOF,TIMEOUT
from gemlogger import logger
from interfaces import IMatlab

'''
Session module provides tools for Hermod to run programs in different
interpretors.
'''

class matlab:
    ''' 
    Matlab gives control over a MATLAB session. It provides a simple interface
    to MATLAB in python by the classmethod command.

    This is how to use it:
    a = matlab()
    a.command('1+1')
    a.close()
    '''

    def __init__(self,args=['-nodisplay'],prompt=['>','>',' '],outputFile=sys.stdout,errorFile=sys.stderr,echo=True,cwd=os.path.expanduser('~')):
        '''
        args - list of optional parameters
        prompt - the matlab prompt
        outputFile - file to print matlab ouputs
        errorFile - error go to this file
        echo - whether or not to print commands
        cwd - current working directory
        '''
        self.prompt = prompt
        self.outputFile = outputFile
        self.errorFile = errorFile
        self.echo = echo
        program = ['/usr/local/bin/matlab']
        program.extend(args)
        self.matlab = subprocess.Popen(program,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=cwd)
        self.listen()

    def close(self):
        '''
        end a session
        '''
        if self.matlab.poll() is None:
            self.matlab.stdin.write('quit\n')
            self.matlab.wait()
        error=self.matlab.stderr.readlines()
        self.errorFile.writelines(error)
        if self.matlab.returncode==0:
            self.outputFile.write('HermodInfo: Matlab exited normally\n')
            self.ok = True
        else:
            self.errorFile.write('HermodError: Matlab exited with errors, exitcode: %i\n'%(self.matlab.returncode))
            self.ok = False

    def listen(self):
        '''
        prints all matlab output to the outputFile, defined in __init__, stops
        at the prompt.
        '''
        queue = ['','','']
        while self.matlab.poll() is None:
            queue.append(self.matlab.stdout.read(1))
            self.outputFile.write(queue.pop(0))
            if queue == self.prompt:
                break
        else:
            for i in queue:
                self.outputFile.write(queue.pop(0))
            self.outputFile.writelines(self.matlab.stdout.readlines())
 
    def command(self,command):
        '''
        send a command to matlab. and wait until its finished
        '''
        if self.matlab.poll() is None:
            self.matlab.stdin.write(command+'\n')
            if self.echo:
                self.outputFile.write('>> %s\n' %command)
            self.listen()

    def commands(self,cmds):
        '''
        send a list of commandstrings to matlab
        '''
        for i in cmds:
            self.command(i)

class matlab_nonblockread(matlab):
    def __init__(self,args=['-nodisplay'],prompt=['>','>',' '],outputFile=sys.stdout):
        self.prompt = prompt
        self.outputFile = outputFile
        program = ['matlab']
        program.extend(args)
        self.matlab = subprocess.Popen(program,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        fcntl.fcntl(self.matlab.stdout,fcntl.F_SETFL,os.O_NONBLOCK)
        self.listen()

    def listen(self):
        queue = ['','','']
        while True:
            try:
                queue.append(self.matlab.stdout.read(1))
                self.outputFile.write(queue.pop(0))
            except IOError,inst:
                if inst.errno==11:
                    pass
                else:
                    raise IOError(inst)
            if queue == self.prompt:
                break
def pbsFactory(orbit,freqmode,calibration,fqid,name,qsmr,db):
    if qsmr=='2-1':
        return pbs_21(orbit,freqmode,calibration,fqid,name,qsmr,db)
    elif qsmr=='2-0':
        return pbs_20(orbit,freqmode,calibration,fqid,name,qsmr,db)
    else:
        return None


class GEMMatlab(IMatlab):

    @logger
    def start_matlab(self):
        self.m_session = spawn('/usr/local/bin/matlab',['-nodisplay'],
                timeout=600)
        self.pattern = self.m_session.compile_pattern_list(
            ['^.*(\?\?\? .*)>> $',
            '^.*(Warning: .*)>> $',
            '^(.*)>> $',
            EOF,
            TIMEOUT])
        return self.m_session.expect(self.pattern)==2

    @logger
    def close_matlab(self):
        self.m_session.sendline('quit')
        return self.m_session.expect(self.pattern)==3

    @logger
    def matlab_is_open(self):
        return self.m_session.isalive()

    @logger
    def matlab_command(self,command,timeout=900):
        self.m_session.sendline(command)
        index = self.m_session.expect(self.pattern,timeout=timeout)
        if index in (1,3,4):
            raise HermodWarning(self.m_session.match.group(1))
        elif index==0:
            raise HermodError(self.m_session.match.group(1))
        return self.m_session.match.group(1)


class pbs:
    '''
    Generic class for running inversions, specialised classes can be base by
    this by inheritance, se this class as a abstract class
    '''
    def __init__(self,orbit,freqmode,calibration,fqid,name,qsmr,db):
        self.orbit = int(orbit)
        self.fqid = int(fqid)
        self.freqmode = int(freqmode)
        self.name = name
        self.calibration = int(calibration)
        self.qsmr = qsmr
        self.dir=''
        self.db = db
        try:
            self.l2p = level2Factory(self.orbit,self.freqmode,self.calibration,self.fqid,self.qsmr,db)
        except HermodError,inst:
            raise HermodError('Error initiating level2: %s' %(inst))

    def prepare(self):
        if self.l2p is not None:
            self.l2p.setFileNames()
            self.l2p.preClean()
        try:
            #prologue.user created the /tmp/tmp{jobid} directory.
            self.dir = '/tmp/tmp%s' % os.environ['PBS_JOBID'].split('.')[0]
            print "assigned tempdir",self.dir
        except :
            try:
                self.dir=tempfile.mkdtemp()
                print >> sys.stderr,"Hermod Warning: created random tempdir",self.dir
            except EnvironmentError,e:
                raise HermodError("Error while creating tempdir: %i, %s, %s" %(e.errno,e.strerror,e,filename))

    def run(self):
        mat = matlab(args=['-nojvm','-nosplash'],cwd='/home/odinop/Matlab/Qsmr_%s'%(self.qsmr.replace('-','_')))
        mat.commands(["set(gcf,'Visible','off')","qsmr_startup","qsmr_inv_op('%s','%0.4X','%0.4X','%s')"%(self.name,self.orbit,self.orbit,self.dir),"close all","clear all","clear all"])
        mat.close()


    def clean(self):
        pass

    def write(self):
        try:
            if self.l2p is not None:
                self.l2p.readAuxFile()
                self.l2p.readData()
                self.l2p.addData()
                self.l2p.cleanFiles()
        except HermodError,inst:
            raise HermodError('write l2data: %s' %(inst))

    def upload(self):
        self.l2p.upload()

class pbs_20(pbs):
    def run(self):
        mat = matlab(args=['-nojvm','-nosplash'],cwd='/home/odinop/Matlab/Qsmr_%s'%(self.qsmr.replace('-','_')))
        mat.commands(["display 'this i a special class designed for qsmr-2-1'","set(gcf,'Visible','off')","qsmr_startup","qsmr_inv_op('%s','%0.4X','%0.4X','%s')"%(self.name,self.orbit,self.orbit,self.dir),"close all","clear all","clear all"])
        mat.close()

class pbs_21(pbs):
    def run(self):
        mat = matlab(args=['-nojvm','-nosplash'],cwd='/home/odinop/Matlab/Qsmr_%s'%(self.qsmr.replace('-','_')))
        mat.commands(["display 'this i a special class designed for qsmr-2-1'","set(gcf,'Visible','off')","qsmr_startup","qsmr_inv_op('%s','%0.4X','%0.4X','%s')"%(self.name,self.orbit,self.orbit,self.dir),"close all","clear all","clear all"])
        mat.close()


def main():
    a = matlab(args=['-nojvm','-nosplash'],outputFile=open('matlab.log','w'))
    a.commands(['1+1','ver'])
    for i in range(2048):
        a.command('%i*%i'%(i,i))
    a.close()

if __name__=='__main__':
    main()

