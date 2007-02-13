#!/usr/bin/python
# vim: set fileencoding=utf-8 :
          
from distutils.core import setup,Extension
setup(name='hermod',
        version='1.2.0',
        package_dir={'hermod': ''},
        packages=['hermod', 'hermod.l1b','hermod.l2','hermod.pdc'],
        description = 'Routines to simplify and improve speed of odinprocessing',
        author='Joakim Möller',
        author_email='joakim.moller@chalmers.se',
        url='http://diamond.rss.chamers.se',
        scripts=['scripts/insertFiles','scripts/readFreq','scripts/rerunOrbits','scripts/getL1b'],
        data_files=[('/etc',['hermod.cfg.default'])],
        ext_modules = [
        Extension('hermod.l1b.ReadHDF', 
            ['l1b/readhdfmodule.c'], 
            libraries = ['mfhdf','df','jpeg','z'] 
            ) 
        ] 
        )

