#!/usr/bin/python
# vim: set fileencoding=utf-8 :
from setuptools import setup,find_packages,Extension

setup(
        name='odin.hermod',
        version='3.3.0',
        description = 'Routines to simplify and improve speed of odinprocessing',
        entry_points= {"console_scripts": [
            "hermodgetlevel1 = odin.hermod.level1:main",
            "hermodrunprocessor = odin.hermod.processor:main",
            "hermodrunjob = odin.hermod.scripts.hermodrunjob:main",
            "hermodgetwinds = odin.hermod.ecmwf:rungetfilesfromnilu",
#            "hermodl1bfind = odin.hermod.scripts.hermodl1bfind:main",
#            "hermodl1bcp = odin.hermod.scripts.hermodl1bcp:main",
#            "hermodl2find = odin.hermod.scripts.hermodl2find:main",
#            "hermodl2cp = odin.hermod.scripts.hermodl2cp:main",
            ]},
        packages = find_packages(),
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
        install_requires=['setuptools','mysql-python','pexpect'],
        tests_require=['mocker','setuptools'],
)

