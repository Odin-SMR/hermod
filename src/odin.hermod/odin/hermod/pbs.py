from subprocess import Popen,PIPE
from os.path import join,expanduser
from interfaces import IPbs
from odin.config.environment import config

runscript = """
#PBS -N %(jobname)s
#PBS -l walltime=%(process_time)s,nice=19,nodes=1:hermod:node
#PBS -q %(queue)s
#PBS -e %(errfile)s
#PBS -o %(outfile)s
#PBS -d %(workdir)s
#PBS -v id=%(id)i,orbit=%(orbit)i,fqid=%(fqid)s,version=%(version)s,backend=%(backend)s,calversion=%(calversion)s,name=%(name)s,process_time=%(process_time)s,LD_LIBRARY_PATH=/opt/matlab/bin/glnxa64

/home/odinop/sandbox/bin/hermodrunjob
"""

class GEMPbs(IPbs):
    
    def set_submit_info(self,queue='new'):
        self.conf = config()

        self.info['queue'] = queue
        self.info['jobname'] =  'o%(orbit).4X%(calversion).1f%(fqid).2i%(version)s' % self.info
        self.info['errfile'] = join(expanduser('~'),'logs', 
                self.info['jobname']+'.err')
        self.info['outfile'] = join(expanduser('~'),'logs',
                self.info['jobname']+'.out')
        self.info['workdir'] = join(expanduser('~'),'Matlab',
                'Qsmr_%s'%self.info['version'].replace('-','_')) 
            


    def submit(self):
        s = Popen([self.conf.get('pbs','batch_command')],stderr=PIPE,
                stdin=PIPE,stdout=PIPE)
        s.stdin.write(runscript%self.info)
        s.stdin.close()
        print s.stdout.read()
        print s.stderr.read()
        s.stdout.close()
        s.stderr.close()



