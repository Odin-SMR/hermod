#!/usr/bin/python
# vim: set fileencoding=utf-8 :
          
from distutils.command.install_data import install_data as _install_data
from distutils.core import setup,Extension
from subprocess import call
from os.path import join

class install_data(_install_data):
    def run(self):
        _install_data.run(self)
        basedir = '/var/lib/torque/mom_priv'
        print "changing mode on healthcheck, prologue, epilogue and config to 500"
        status = call(['chmod','-f','500',join(basedir,'epilogue'),join(basedir,'healthcheck'),join(basedir,'prologue'),join(basedir,'config')])
        print "changing mode on epilogue.user, epilogue.precancel and prologue.user to 505"
        status = call(['chmod','-f','505',join(basedir,'epilogue.user'),join(basedir,'epilogue.precancel'),join(basedir,'prologue.user')])
        status = call(['/etc/init.d/torque-mom','reload'])


setup(cmdclass={'install_data': install_data},
        name='hermod',
        version='2.4.2',
        package_dir={'hermod': ''},
        packages=['hermod'],
        description = 'Routines to simplify and improve speed of odinprocessing',
        author='Joakim Möller',
        author_email='joakim.moller@chalmers.se',
        url='http://odin.rss.chalmers.se',
        scripts=['scripts/hermodwritel22db','scripts/hermodrerun','scripts/hermodgetl1','scripts/hermodlastdays','scripts/hermodgetweather','pbs_scripts/healthcheck','scripts/hermodrunjob','scripts/hermodl1bcp','scripts/hermodl1bfind','scripts/hermodl2cp','scripts/hermodl2find'],
        data_files=[('/etc',['hermod.cfg.default']),('/var/lib/torque',['pbs_scripts/torque.cfg','pbs_scripts/server_name']),('/var/lib/torque/mom_priv',['pbs_scripts/config','pbs_scripts/epilogue.precancel','pbs_scripts/epilogue','pbs_scripts/prologue','pbs_scripts/epilogue.user','pbs_scripts/prologue.user','pbs_scripts/healthcheck'])]
#        ,ext_modules = [
#        Extension('hermod.l1b.ReadHDF', 
#            ['l1b/readhdfmodule.c'], 
#            libraries = ['mfhdf','df','jpeg','z'] 
#            ) 
#        ] 
        )

