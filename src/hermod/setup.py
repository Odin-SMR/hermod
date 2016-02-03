#!/usr/bin/python
# vim: set fileencoding=utf-8 :
from setuptools import setup,find_packages,Extension

setup(
		name='hermod',
		version='0.0.1',
		description = 'Routines to simplify and improve speed of odinprocessing',
		entry_points= {"console_scripts": [
		"hermodl1binserter = hermod.level1inserter:main",
		]},
		packages = find_packages(exclude=['ez_setup','tests']),
		package_data={'hermod': [
			'hermod.cfg.default'
				]},
				include_package_data=True,

				test_suite='hermod.tests',
				zip_safe=True,
				author='Joakim Möller',
				author_email='joakim.moller@molflow.com',
				url='http://odin.rss.chalmers.se',
				install_requires=[
				'setuptools',
				'sqlalchemy',
				],
				)

