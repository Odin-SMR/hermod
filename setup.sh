#! /bin/bash
# This setup file is meant to be run when setting up the Hermod base system
# Docker container, to automatically install all our Python modules in the
# container.
# By default the modules are installed using the "develop" keyword, which means
# that they are linked dynamically to the source directory and can be updated
# "on the fly". For release versions the "install" keyword should instead be
# used, in order to produce a self-contained environment.

# Store the root of the Hermod repository:
HERMOD_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Install the Python modules:
echo "-------------------------"
echo " Installing odin.config: "
echo "-------------------------"
cd $HERMOD_ROOT/src/odin.config/
python setup.py develop
echo " "

echo "------------------------"
echo " Installing odin.ecmwf: "
echo "------------------------"
cd $HERMOD_ROOT/src/odin.ecmwf/
python setup.py develop
echo " "

echo "-------------------------"
echo " Installing odin.hermod: "
echo "-------------------------"
cd $HERMOD_ROOT/src/odin.hermod/
python setup.py develop
echo " "

echo "------------------------"
echo " Installing odin.iasco: "
echo "------------------------"
cd $HERMOD_ROOT/src/odin.iasco/
python setup.py develop
echo " "

cd $HERMOD_ROOT

echo "Done"
