#!/usr/bin/python
# vim: set fileencoding=utf-8 :
from setuptools import setup, find_packages

setup(
    name='hermod',
    version='0.0.2',
    description='Routines to simplify and improve speed of odinprocessing',
    entry_points={
        "console_scripts": [
            "hermodl1binserter = hermod.level1inserter:main",
            ]
    },
    packages=find_packages(exclude=['ez_setup', 'tests']),
    zip_safe=True,
    author='Joakim Möller',
    author_email='joakim.moller@molflow.com',
    url='http://odin.rss.chalmers.se',
    install_requires=[
        'setuptools',
    ],
)

