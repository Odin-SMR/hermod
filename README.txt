=======
Hermod
=======


Installation of Hermod.
=======================

Hermod is available for download at GEMM's subversion repository.

  svn checkout http://svn.rss.chalmers.se/svn/odinsmr/hermod/trunk hermod


Ubuntu 12.04.04
----------------

Some essential packages are needed to build hermod

  sudo apt-get install build-essential git-svn bison flex gfortran libatlas-base-dev python-dev pkg-config cmake python-virtualenv python-zc.buildout

Hermod uses buildout to build all dependencies

  cd hermod
  python2.7 bootstrap.py -v 1.5.2
  bin/buildout

