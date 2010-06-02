#!/usr/bin/python
# vim: set fileencoding=utf-8 :
from setuptools import setup,find_packages,Extension

setup(
        name='odin.config',
        version='0.0.2',
        description = 'Routines to simplify and improve speed of odinprocessing',
        data_files=[('odin/config',['odin/config/defaults.cfg','odin/config/odinlogger.cfg']),],
	packages = find_packages(),
	namespace_packages = ['odin'],
        test_suite='hermod.config.tests.alltests.test_suite',
        zip_safe=False,
        author='Joakim Möller',
        author_email='joakim.moller@chalmers.se',
        url='http://odin.rss.chalmers.se',
        install_requires=['setuptools'],
        #tests_require=['mocker','setuptools'],
)

