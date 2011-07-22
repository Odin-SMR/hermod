#!/usr/bin/python
# vim: set fileencoding=utf-8 :
from setuptools import setup,find_packages

setup(
        name='odin.ecmwf',
        version='1.1.1',
        description = 'Receives and converts gribfiles from ecmwf',
        entry_points= {"console_scripts": [
            "hermodcreateecmwf = odin.ecmwf.create_odinecmwf:create_insert",
            ]},
        packages = find_packages(exclude=['ez_setup','tests']),
        namespace_packages = ['odin'],
        package_data={'odin.ecmwf': [
                'odinecmwf/odinecmwf_grib2.so',
                'odinecmwf/odinecmwf_grib1.so'
                ]},
        include_package_data=True,

        test_suite='odin.ecmwf.tests.test_all.test_suite',
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

