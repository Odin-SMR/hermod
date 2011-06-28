#!/usr/bin/python
# vim: set fileencoding=utf-8 :
from setuptools import setup,find_packages,Extension

setup(
        name='odin.ecmwf',
        version='1.0.0',
        description = 'Receives and converts gribfiles from ecmwf',
        entry_points= {"console_scripts": [
            "hermodgetlevel1 = odin.hermod.l1b:downloadl1bfiles",
            ]},
        packages = find_packages(),
        namespace_packages = ['odin'],
        test_suite='odin.ecmwf.tests.alltests.test_suite',
        zip_safe=True,
        author='Joakim Möller',
        author_email='joakim.moller@molflow.com',
        url='http://odin.rss.chalmers.se',
        install_requires=[
            'setuptools',
            'mysql-python==1.2.3',
            'odin.config',
		],
        tests_require=['mocker','setuptools'],
)

