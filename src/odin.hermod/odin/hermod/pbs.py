from subprocess import Popen, PIPE
from os.path import join, expanduser
from interfaces import IPbs
from odin.config.environment import config as odin_config

runscript = """
#PBS -N %(jobname)s
#PBS -l walltime=%(process_time)s,nodes=1:hermod:node:precise,mem=950mb
#PBS -q %(queue)s@%(torquehost)s
#PBS -e %(errfile)s
#PBS -o %(outfile)s
#PBS -d %(workdir)s
#PBS -v id=%(id)i,orbit=%(orbit)i,fqid=%(fqid)s,version=%(version)s,backend=%(backend)s,calversion=%(calversion)s,name=%(name)s,process_time=%(process_time)s,LD_LIBRARY_PATH=/opt/matlab/bin/glnxa64

umask 027
/home/odinop/hermod_production/bin/hermodrunjob
#docker exec -d odinop_hermod_1 hermodrunjob id=%(id)i,orbit=%(orbit)i,fqid=%(fqid)s,version=%(version)s,backend=%(backend)s,calversion=%(calversion)s,name=%(name)s,process_time=%(process_time)s,LD_LIBRARY_PATH=/opt/matlab/bin/glnxa64
"""
# the runscript is not generic enough - have to change the last line


class GEMPbs(IPbs):

    def set_submit_info(self, queue='new'):
        self.conf = odin_config()

        self.info['queue'] = queue
        self.info['torquehost'] = self.conf.get("TORQUE", "torquehost")
        jobname = ('o%(orbit).4X%(calversion).1f%(fqid).2i%(version)s' %
                   self.info)
        self.info['jobname'] = jobname
        self.info['errfile'] = join(expanduser('~'), 'logs',
                                    self.info['jobname'] + '.err')
        self.info['outfile'] = join(expanduser('~'), 'logs',
                                    self.info['jobname'] + '.out')
        self.info['workdir'] = join(expanduser('~'), 'Matlab',
                                    'Qsmr_%s' %
                                    self.info['version'].replace('-', '_'))

    def submit(self):
        s = Popen([self.conf.get('pbs', 'batch_command')], stderr=PIPE,
                  stdin=PIPE, stdout=PIPE)
        s.stdin.write(runscript % self.info)
        s.stdin.close()
        print s.stdout.read()
        print s.stderr.read()
        s.stdout.close()
        s.stderr.close()
