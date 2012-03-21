#test setup.py
from setuptools import setup, find_packages
setup(
	name = "pyPV2EQL",
	description="Python scripts for reading ECMWF files, calculating EQL and writing into Matlab files",
	version = "0.1",
	author="Kazutoshi Sagi",
	author_email="sagi@chalmers.se",
	packages = find_packages(),
	)