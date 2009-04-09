from subprocess import Popen,PIPE
from os.path import join,expanduser

from MySQLdb.cursors import DictCursor

from interfaces import IPbs

runscript = """
#PBS -N %(jobname)s
#PBS -l walltime=%(process_time)s,nice=19,nodes=1:hermod:node
#PBS -q %(queue)s
#PBS -e %(errfile)s
#PBS -o %(outfile)s
#PBS -d %(workdir)s
#PBS -v id=%(id)i,orbit=%(orbit)i,fqid=%(fqid)s,version=%(version)s,backend=%(backend)s,calversion=%(calversion)s,name=%(name)s,process_time=%(process_time)s

PYTHONPATH=/home/joakim/workspace/hermod python /home/joakim/workspace/hermod/scripts/hermodrunjob.py
"""


class GEMPbs(IPbs):
    
    def set_submit_info(self,queue='new'):
        self.info['queue'] = queue
        self.info['jobname'] =  'o%(orbit).4X%(calversion).1f%(fqid).2i%(version)s' % self.info
        self.info['errfile'] = join(expanduser('~'),'logs', 
                self.info['jobname']+'.err')
        self.info['outfile'] = join(expanduser('~'),'logs',
                self.info['jobname']+'.out')
        self.info['workdir'] = join(expanduser('~'),'Matlab',
                'Qsmr_%s'%self.info['version'].replace('-','_')) 
            


    def submit(self):
        s = Popen(['/usr/bin/qsub'],stderr=PIPE,stdin=PIPE,stdout=PIPE)
        s.stdin.write(runscript%self.info)
        s.stdin.close()
        print s.stdout.read()
        print s.stderr.read()
        s.stdout.close()
        s.stderr.close()



