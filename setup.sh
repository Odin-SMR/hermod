#! /bin/bash

# Store the root of the Hermod repository:
HERMOD_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

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
