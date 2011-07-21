#!/usr/bin/python
# vim: set fileencoding=utf-8 :
from setuptools import setup,find_packages

setup(
        name='odin.config',
        version='0.0.5',
        description = 'Routines to simplify and improve speed of odinprocessing',
	packages = find_packages(exclude=['ez_setup','tests']),
        package_data={'odin.config':['defaults.cfg','odinlogger.cfg']},
        include_package_data=True,
	namespace_packages = ['odin'],
        test_suite='odin.config.tests.alltests.test_suite',
        zip_safe=False,
        author='Joakim Möller',
        author_email='joakim.moller@chalmers.se',
        url='http://odin.rss.chalmers.se',
        install_requires=[
            'setuptools',
            'mysql-python==1.2.3',
            ]
        #tests_require=['mocker','setuptools'],
)

