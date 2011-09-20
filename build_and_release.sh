#!/bin/bash

packages=`find src/odin.* -type f -name setup.py | cut -d/ -f1-2`
base=`pwd`
for pkg in $packages
do
	echo
	echo ************* $pkg ************
	echo
	cd $pkg
	../../bin/odinpy setup.py bdist_egg
	echo *****************
	echo ** releasing $pkg
	echo *****************
	find . -type f -regex .*egg -ctime -1 -exec cp -v \{\} /misc/apps/odinsite \;
	cd $base
done
