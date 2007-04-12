#!/usr/bin/python
# vim: set fileencoding=utf-8 :
          
from distutils.core import setup,Extension
from subprocess import call
from os.path import join

setup(name='hermod',
        version='1.3.0.rc1',
        package_dir={'hermod': ''},
        packages=['hermod', 'hermod.l1b','hermod.l2','hermod.pdc'],
        description = 'Routines to simplify and improve speed of odinprocessing',
        author='Joakim Möller',
        author_email='joakim.moller@chalmers.se',
        url='http://diamond.rss.chalmers.se',
        scripts=['scripts/insertFiles','scripts/readFreq','scripts/rerunOrbits','scripts/getL1b','scripts/statuslastdays','scripts/orbitslastdays','scripts/getWeather','pbs_scripts/healthcheck'],
        data_files=[('/etc',['hermod.cfg.default']),('/var/spool/PBS',['pbs_scripts/torque.cfg','pbs_scripts/server_name']),('/var/spool/PBS/mom_priv',['pbs_scripts/config','pbs_scripts/epilogue.precancel','pbs_scripts/epilogue','pbs_scripts/prologue','pbs_scripts/epilogue.user','pbs_scripts/prologue.user','pbs_scripts/healthcheck'])],
        ext_modules = [
        Extension('hermod.l1b.ReadHDF', 
            ['l1b/readhdfmodule.c'], 
            libraries = ['mfhdf','df','jpeg','z'] 
            ) 
        ] 
        )
basedir = '/var/spool/PBS/mom_priv'
status = call(['chmod','-f','500',join(basedir,'epilogue.precancel'),join(basedir,'epilogue'),join(basedir,'prologue'),join(basedir,'config')])
status = call(['chmod','-f','505',join(basedir,'epilogue.user'),join(basedir,'prologue.user')])
status = call(['/etc/init.d/pbs','restart'])

