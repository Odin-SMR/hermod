#!/usr/bin/python
# vim: set fileencoding=utf-8 :
from setuptools import setup,find_packages,Extension

setup(
		name='odin.hermod',
		version='3.4.6',
		description = 'Routines to simplify and improve speed of odinprocessing',
		entry_points= {"console_scripts": [
		"hermodgetlevel1 = odin.hermod.l1b:downloadl1bfiles",
		"hermodrunprocessor = odin.hermod.processor:main",
		"hermodrunjob = odin.hermod.scripts.hermodrunjob:main",
		"hermodgetwinds = odin.hermod.ecmwf:rungetfilesfromnilu",
		"hermodmakezpt = odin.hermod.winds:makewinds",
		"hermodmount = odin.hermod.smr:main",
		"hermodrelink = odin.hermod.link_db:main",
#            "hermodl1bfind = odin.hermod.scripts.hermodl1bfind:main",
#            "hermodl1bcp = odin.hermod.scripts.hermodl1bcp:main",
#            "hermodl2find = odin.hermod.scripts.hermodl2find:main",
#            "hermodl2cp = odin.hermod.scripts.hermodl2cp:main",
		"hermodlastdays_ecmwf = odin.hermod.scripts.hermod_diag:last_ecmwf",
		"hermodlastdays_l1b = odin.hermod.scripts.hermod_diag:last_l1b",
		"hermodlastdays_l2 = odin.hermod.scripts.hermod_diag:last_l2",
		"hermodlist_ecmwf = odin.hermod.scripts.hermod_diag:list_ecmwf",
		"hermodlist_l1b_pdc = odin.hermod.scripts.hermod_diag:list_l1b_pdc",
		"hermodlist_l1b = odin.hermod.scripts.hermod_diag:list_l1b",
		"hermodlist_l1bzpt = odin.hermod.scripts.hermod_diag:list_l1bzpt",
		"hermodlist_l2 = odin.hermod.scripts.hermod_diag:list_l2",
		]},
		packages = find_packages(exclude=['ez_setup','tests']),
		namespace_packages = ['odin'],
		package_data={'odin.hermod': [
			'hermod.cfg.default'
				]},
				include_package_data=True,

				test_suite='odin.hermod.tests.test_all',
				zip_safe=False,
				author='Joakim Möller',
				author_email='joakim.moller@chalmers.se',
				url='http://odin.rss.chalmers.se',
				install_requires=[
				'setuptools',
				'mysql-python',
				'pexpect',
				'fuse-python',
				'pyhdf',
				'numpy',
				'scipy',
				'matplotlib',
				'pymatlab',
				'netCDF4',
				'odin.config',
				'pymatlab',
                                'torquepy',
				],
				tests_require=['mocker','setuptools'],
				)

