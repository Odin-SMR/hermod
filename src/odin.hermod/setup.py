#!/usr/bin/python
# vim: set fileencoding=utf-8 :
from setuptools import setup,find_packages,Extension

setup(
        name='odin.hermod',
        version='3.3.13',
        description = 'Routines to simplify and improve speed of odinprocessing',
        entry_points= {"console_scripts": [
            "hermodgetlevel1 = odin.hermod.l1b:downloadl1bfiles",
            "hermodrunprocessor = odin.hermod.processor:main",
            "hermodrunjob = odin.hermod.scripts.hermodrunjob:main",
            "hermodgetwinds = odin.hermod.ecmwf:rungetfilesfromnilu",
            "hermodmakezpt = odin.hermod.winds:makewinds",
            "hermodmount = odin.hermod.smr:main",
	    "hermodrelink = odin.hermod.scripts.relink:relink",
#            "hermodl1bfind = odin.hermod.scripts.hermodl1bfind:main",
#            "hermodl1bcp = odin.hermod.scripts.hermodl1bcp:main",
#            "hermodl2find = odin.hermod.scripts.hermodl2find:main",
#            "hermodl2cp = odin.hermod.scripts.hermodl2cp:main",
            ]},
        packages = find_packages(exclude=['ez_setup','tests']),
        package_data={'odin.hermod': [
                'hermod.cfg.default'
                ]},
        namespace_packages = ['odin'],
        ext_modules=[Extension('odin.hermod.torque',
                      ['odin/hermod/pbs.c'],
                      libraries=['torque'],
                      include_dirs=['/usr/local/pbs/include','/usr/include/torque'],
                      library_dirs=['/usr/local/pbs/lib','/usr/lib'],
                      )],
        test_suite='odin.hermod.tests.alltests.test_suite',
        zip_safe=False,
        author='Joakim Möller',
        author_email='joakim.moller@chalmers.se',
        url='http://odin.rss.chalmers.se',
        install_requires=[
            'setuptools',
            'mysql-python==1.2.3',
            'pexpect==2.4',
            'fuse-python==0.2',
            'pyhdf==0.8.3',
            'numpy==1.3.0',
            'scipy==0.7.0',
            'matplotlib==0.99.1.1',
            'pymatlab==0.1.3',
            'odin.config',
		],
        tests_require=['mocker','setuptools'],
)

