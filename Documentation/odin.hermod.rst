=======================
HERMOD processing suite
=======================

:Authors: 

        Joakim Möller <joakim.moller@chalmers.se>

:Version: 
        
        0.1 


:Date:

        2010-03-23

:Abstract: 

        HERMOD is a part of the ODIN processing chain - automating level1b data to level2 data. This document describes the installation, configuration and function of the program suite. In short HERMOD sets up and run SMR in the ODIN cluster environment.

.. raw:: pdf
        
        PageBreak

.. contents:: 
.. target-notes::
.. sectnum::

Level2 processing chain - HERMOD
================================

.. The processing chain program suite is a set of python modules that provides an
.. information system that makes it possible to track every single SMILES level1
.. scan and choose a suitable processor to make higher level data ie. LEVEL2 data.
.. 
.. JUNO is a part of the SMILES processing chain makeing high level information
.. from raw satelite data to very highlevel data ie. Human understandable data and
.. possibly data collected and aggragated over longer timeperiods.
.. 
.. Overview
.. --------
.. 
.. The JUNO suite are written mostly in Python_ and small part of the code is
.. written in C with Python's C-api to extend Pythons capabilities to
.. interact with different tools in the Processing chain.
.. 
.. Meta data from the calculations made by AMATERASU is stored in a database and
.. data are stored in files at the filesystem. 
.. 
.. JUNO is the working name of the processing chain. It was chosen for fun after
.. an attack of the smiles computers. The name of the attackers program was
.. JUNO.  The name JUNO is unfortunately already occupied in the `Python Package
.. Index`__ name space. A new must be chosen if we want to publish it at the
.. `Python Package Index`__ or to avoid name clashes when using ``easy_install`` to
.. install the juno packages suite.
.. 
.. The JUNO system can be seen as a set of scripts that glues AMATERASU calculations and its results into the database. JUNO also uses those result to find out what data is missing or what can be calculated for the moment ie. all prerequisits for starting AMATERASU calculations are resolve. JUNO also gather AMATERASU outputs into daily data products into HDF5 files.
.. 
.. .. _Python: http://python.org
.. .. _PyPI: http://pypi.python.org
.. __ PyPI_
.. __ PyPI_


Required dependencies - Installation and configuration
======================================================

.. The SMILES processing chain and JUNO make use of third party software.
.. They are all based on some type of open source license like GNU GPL or BSD
.. license.
.. 
.. MySQL_ :
.. 
..         Relational database to manage metadata. Database design for this
..         project i discussed in `Design of Database`_
.. 
.. Torque_ :
.. 
..         Torque is a Cluster Resource Manager.  Documentation and detailed
..         installation instructions can be found at Torque_ documentation pages.
..         Site specific configuration will be discussed in `Torque
..         configuration`_ section.
.. 
.. Maui_ :
..         
..         The Cluster Scheduler only site specific setup vill be noted in `Maui
..         configuration`_
.. 
.. .. _MySQL: http://dev.mysql.com/doc/refman/5.1/en/
.. .. _Torque: http://www.clusterresources.com/products/torque/docs
.. .. _Maui: http://www.clusterresources.com/products/maui/docs
.. 
 
Design of Database
------------------
 
.. Configuration of database is minimal. Standard apt installation of the package mysql-server is enough see `Appendix A - MySQL create script`_ and `Appendix B - MySQL Table layout`_ for database and table layout.
 
Torque configuration
--------------------
 
.. Two types of Torque installations are required - one server installation and
.. several client installations on each node in the cluster. The server
.. installation manages the queueingsystem and needs to know about all clients
.. (computee nodes) in the cluster. The clients does only need to now about the
.. server.
.. 
.. In the Smiles specific environment all configurational files can be found in
.. ``/var/spool/torque`` for both server and clients. Smiles-p1 is the queueing
.. server and ``smiles-p3``, ``smiles-p4``, ``smiles-p5``, ``smiles-p9``, ``smiles-p10``, ``smiles-p11`` are clients. 
 
Torque client configuration
___________________________
 
.. A standard apt installation of torque-client package is sufficient on each node computer. The following files needs to be edited.
.. 
.. ``torqueserver``:
.. 
.. .. code-block:: none
.. 
..         smiles-p1
.. 
.. ``mom_priv/config``:
.. 
.. .. code-block:: none
.. 
..         $configversion 5
..         $remote_reconfig true
..         $logevent 0x1fff
..         $pbsserver smiles-p1
..         $pbsclient smiles-p1
 
Torque server configuration
___________________________
 
.. A standard apt installation would normaly do fine.
.. 
.. The file ``server_priv/nodea`` defines the computee nodes:
.. 
.. .. code-block:: none
.. 
..         smiles-p3 np=8
..         smiles-p4 np=8
..         smiles-p5 np=16
..         smiles-p9 np=16
..         smiles-p10 np=16
..         smiles-p11 np=16
.. 
.. Some settings are done through torque's configuration program ``qmgr``. A printout of Torque server settings generated with ``qmgr -C 'print server'`` can be found in `Appendix C - Torque server settings`_.
.. 
 
Maui configuration
------------------
 
.. The main configuration file can be found at smiles-p1 in the directory. This software is installed by SEC.
.. 
.. .. code-block:: none
.. 
..         /usr/local/maui/maui.cfg
.. 
..         
.. Full configuration file can be found in `Appendix D - Maui configuration`_.


HERMOD
======

.. Overview
.. --------
.. 
.. JUNO is a program suite written in Python that interacts with AMATERASU and the
.. SMILES DATABASE. JUNO runs regulary and decides when to run AMATERASU according
.. to information JUNO can find in the SMILES DATABASE. JUNO provides a fully
.. automatic processing system for processing data from LEVEL1 to LEVEL2.
.. 
.. Package details
.. ---------------
.. 
.. JUNO is divided into several smaller enteties that provide specific functionality.
.. 
.. juno.hdf5
.. _________
.. 
.. The juno.hdf5 package aggregates AMATERASU LEVEL2 data in to a HDF5 file
.. containing all data from a specific day and species. Normally this program runs
.. from a crontab (launched on a specific time each day) but it runs easily from the command line.
.. 
.. Log in as ``smiles`` on ``smiles-p10``. The command ``hdfwriter`` will find level1 scans and put the in the queue to process level2 data. Output will be placed in ``/mnt/raid0/smilesdata/level2r``.
.. 
.. .. code-block:: none
.. 
..         smiles@smiles-p10:/mnt/raid0/smilesdata/juno$ bin/hdf5writer -h
..         
..         Usage: hdf5writer [options]
..         
..         Aggregates Level2_nict profiles to a HDF EOS file.
..         
..         Options:
..           -h, --help            show this help message and exit
..           -s YYYYMMDD, --start-date=YYYYMMDD
..                                 filter on start date default is 2 days from now
..           -k YYYYMMDD, --end-date=YYYYMMDD
..                                 filter on stop date default is now
..           -b BAND, --band=BAND  only select BAND. Default is all bands
..           -r L2R_VERSION, --l2r-version=L2R_VERSION
..                                 use l2r-version default is latest available
..           -v L1B_VERSION, --l1b-version=L1B_VERSION
..                                 use l2r-version default is std005
..        
.. 
.. Example 1:  Create hdf5 files for 20091109 to 10091110
.. 
.. .. code-block:: none
.. 
..         smiles@smiles-p10:/mnt/raid0/smilesdata/juno$ bin/hdf5writer \
..         -s 20091109 -k 20091110 -r 0.4.3 -v std005
.. 
.. Example 2:  Create hdf5 files for 20091109 to 10091110 only band C and A
.. 
.. .. code-block:: none
.. 
..         smiles@smiles-p10:/mnt/raid0/smilesdata/juno$ bin/hdf5writer -s \
..         20091109 -k 20091110 -bA -bC
.. 
.. juno.pbs
.. ________
.. 
.. This package interfaces with the resource manager TORQUE to put AMATERASU jobs into the batch queue.
.. 
.. Log in as smiles on ``smiles-p1``. The command ``launchjobs`` will find level1 scans and put the in the queue to process level2 data.
.. 
.. .. code-block:: none
.. 
..         smiles@smiles-p1:~/python/smiles$ bin/launchjobs -h
..         Usage: launchjobs [options]
..         
..         Launch L1B scans into cluster.
..         
..         Options:
..           -h, --help            show this help message and exit
..           -s YYYYMMDD, --start-date=YYYYMMDD
..                                 filter on start date default is 2 days from now
..           -k YYYYMMDD, --end-date=YYYYMMDD
..                                 filter on stop date default is now
..           -t TYPE, --type=TYPE  filter on TYPE  default [JAXA_std,JAXA_rev,NICT]
..           -f, --force           Force processing even if level2 already is 
..                                 produced or previous processing ended with 
..                                 errors
..         
.. Example 1: start processing of the 29 of october 2009 (all types)
.. 
.. .. code-block:: none
.. 
..         smiles@smiles-p1:~/python/smiles$ bin/launchjobs -s 20091029 \
..                 -k 20091029
..         
.. Example 2: start processing of the 29 of october 2009 JAXA_rev only
.. 
.. .. code-block:: none
.. 
..         smiles@smiles-p1:~/python/smiles$ bin/launchjobs -s 20091029 \
..                 -k 20091029 -t JAXA_rev
.. 
.. 
.. juno.external
.. _____________
.. 
.. Tool for use outside of NICT's computing environment. To be distributed to people that wants to interact with smiles specific fileformats
.. 
.. This example shows how to convert a single l1b-file to a MATLAB file.
.. 
.. .. code-block:: none
.. 
..         junosavemat -f output.mat l1bfile.l1b
.. 
.. JUNO Installation
.. -----------------
.. 
.. The main installation is located in the ``/mnt/raid0/smilesdata/juno``
.. directory.  From this location all processing nodes runs their instances of
.. JUNO from.  Unfortunately due to different Ubuntu versions installed throught
.. out the computing system smiles-p1 is not using the same directory to run from.
.. This due to different libraries install on different version of ubuntu.
.. Programs running on smiles-p1 runs from ``/home/smiles/python/smiles``
.. 
.. Installing on ubuntu 9.10 requires the following packages.
.. 
.. .. code-block:: none
.. 
..         pyton-dev
..         python-virtualenv
..         python-setuptools
..         subversion
..         libhdf5-serial-dev
..         libatlas-base-dev
..         gfortran
..         libfreetype6-dev
..         libpng12-dev
..         python-wxgtk2.8
..         python-gtk2-dev
..         libmysqlclient-dev
..         libwxgtk2.8-dev
.. 
.. To test if all libraries are available on a machine run the following line. This command generates no output if everything is ok:
.. 
.. .. code-block:: none
.. 
..         find /mnt/raid0/smilesdata/juno/ -regex .*so -exec ldd \{\} + | grep \
..                 "not found" | sort -u
.. 
.. 
.. To make sure our environment does not change and break when the ubuntu system
.. updates. Juno is installed in a virtual environment. This is done with the
.. ubuntu apt package ``virtual-env``. All packages ready for deployment is put in
.. ``/mnt/raid0/smilesdata/distributionfiles`` by the JUNO developers
.. 
.. First time installation:
.. 
.. .. code-block:: none
..         
..         $ virtual-env -p/usr/bin/python2.6 --no-site-packages dir_to_install
..         $ cd dir_to_install
..         $ easy_install --find-links=/mnt/raid0/smilesdata/distributionfiles\
..                  junomain
.. 
.. This will pull a complete installation of latest available JUNO, AMATERASU and dependencies.
.. 
.. Developers installation
.. _______________________
.. 
.. An automatic script to install a developers environment exists. The script will
.. work in Smiles computing environment - on the smiles-pn  machines. Download it
.. an run it:
.. 
.. .. code-block:: none
.. 
..         $ wget http://svn.rss.chalmers.se/svn/smiles//trunk/create_virtualenv.sh
..         $ sh create_virtualenv.sh dir_to_install
.. 
.. This script creates a virtual environment and downloads all source code from
.. the svn server. By running the ``build-all``-script a semi-automated deployment starts building all packages and proposes commands to run for deployment
.. of the JUNO packages in the computing environment.
.. 
.. .. code-block:: none
..         
..         $ dir_to_install/dist_all 
.. 
.. Both script is provided in `Appendix E - Juno scripts` for reference.
.. 
.. The source of all JUNO and AMATERASU is available at `Chalmers' Subversion repoitory`__ .
.. 
.. .. _svn: http://svn.rss.chalmers.se/svn/smiles/
.. __ svn_
.. 
.. Algorithms
.. ----------
.. 
.. Finding scans available for processing
.. ______________________________________
.. 
.. When a scan with the corresponding GEOS5 information is available the scan can
.. be selected for execution (launched to execution queue). There are some
.. constraints — if a level2 file already exists or level2 file already is queued
.. or previous execution ended with an error.
.. 
.. The following query describes it more precisely:
.. 
.. .. code-block:: mysql
.. 
..         SELECT L1b_filename, GEOS5_LEVEL1_filename, date, scan,
..             L1b_version, L1b_type from LEVEL1 
..             natural join GEOS5_LEVEL1
..             natural left join LEVEL2_chain l2
..             where L2_flag=0  and l2.status is Null
..             and GEOS5_flag=1
.. 
.. Queuing and execution
.. _____________________
.. 
.. A "job" is defined from the lookup in the previous section. And information
.. about the processing is sent to a queue for later execution. The Resource
.. system that handles the queue and the execution nodes in the computing cluster
.. (``smiles-p3``, ``smiles-p4``, ``smiles-p5,...``) is Torque_. 
.. Basically the "job" is a shell script sent to another machine for execution.
.. 
.. The script ``launchjobs`` described in juno.pbs_ puts  the script ``junorunner`` in queue with different input parameters to  run on the computee nodes.
.. 
.. Processing
.. __________
.. 
.. The ``launchjobs``-script executes the main-function in ``juno.common.scan`` which is running AMATERASU and collect the results and puts them in the dabase and the filesystem.
.. 
.. Appendix A - MySQL Create script
.. ================================
.. 
.. This script is available at the SMILES svn-repository_
.. 
.. .. _svn-repository: http://svn.rss.chalmers.se/svn/smiles/branches/jmbranch2/docs/database_model.sql
.. 
.. Appendix B - MySQL Table layout
.. ===============================
.. 
.. .. image:: database_model.png
.. 
.. Appendix C - Torque server settings
.. ===================================
.. 
.. .. code-block:: none
..         :include: pbs_set_server.conf
.. 
.. Appendix D - Maui configuration
.. ===============================
.. 
.. The only configuration file is in /usr/local/maui.cfg:
.. 
.. .. code-block:: none
..         :include: maui.cfg
.. 
.. Appendix E - Juno scripts
.. =========================
.. 
.. Developers installation script:
.. 
.. .. code-block:: none
..         :include: create_virtualenv.sh
.. 
.. Automated deployment:
.. 
.. .. code-block:: none
..         :include: dist_all.sh
.. 
.. .. raw:: pdf
.. 
..         PageBreak
