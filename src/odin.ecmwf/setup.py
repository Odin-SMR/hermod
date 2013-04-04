#!/usr/bin/python
# vim: set fileencoding=utf-8 :
from setuptools import setup,find_packages

setup(
        name='odin.ecmwf',
        version='1.4.8',
        description = 'Receives and converts gribfiles from ecmwf',
        entry_points= {"console_scripts": [
            "hermodcreateecmwf = odin.ecmwf.create_odinecmwf:create_insert",
            "hermodcreateptz  =  odin.ecmwf.create_ptz:main",
            "hermodcreatelait = odin.ecmwf.create_lait:create_insert",
            "hermodlist = odin.ecmwf.list_not_downloaded:main",
            ]},
        packages = find_packages(exclude=['ez_setup','tests']),
        namespace_packages = ['odin'],
        package_data={'odin.ecmwf': [
                'odinecmwf/odinecmwf_grib2.so',
                'cira.mat',
                ]},
        include_package_data=True,

        test_suite='odin.ecmwf.tests.test_all',
        zip_safe=True,
        author='Joakim Möller',
        author_email='joakim.moller@molflow.com',
        url='http://odin.rss.chalmers.se',
        install_requires=[
            'setuptools',
            'mysql-python',
            'odin.config',
            'numpy',
            'scipy',
            'netCDF4',
		],
        tests_require=['mocker','setuptools'],
)

