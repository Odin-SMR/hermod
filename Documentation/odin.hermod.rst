=======================
HERMOD processing suite
=======================

:Authors: 

        Joakim Möller <joakim.moller@molflow.com>, Donal Murtagh
        <donal.murtagh@chalmers.se>, Joachim Urban <joaurb@chalmers.se>

:Version: 
        
        0.2 


:Date:

        2010-10-01

:Abstract: 

        Hermod is a part of the Odin processing chain - automating level1b data
        to level2 data. This document describes the installation, configuration
        and function of the program suite. In short Hermod prepares
        requirements such as external datafiles and launches a Qsmr session
        when all requirements are met.

.. .. raw:: pdf
..        
..        PageBreak

.. contents:: 
.. target-notes::
.. sectnum::

Level2 processing chain - Hermod
================================

The processing chain program suite is a set of python modules that provides an
information system that makes it possible to track every single Odin Level1
file and choose a suitable processor to make higher level data i.e. Level2
data.
 
Hermod is a part of the Odin processing chain making high level information
from calibrated satelite data to very highlevel data ie. Human understandable
data and possibly data collected and aggragated over longer timeperiods.

Overview
--------

.. image:: flow.png
    :height: 5cm

The hermod suite are written mostly in Python_ and small part of the code is
written in C with Python's C-api to extend Pythons capabilities to
interact with different tools in the Processing chain.

Meta data from calculations made by Qsmr is stored in a database and
data is stored in files at the filesystem. 

Hermod is the collection name for the processing chain. The name Hermod was
chosen after one of the sons of Odin - Hermod known for his speed. 

The Hermod processing system can be seen as a set of scripts that glues Qsmr's
calculations and its results into the database. Hermod also uses those result
to find out what data is missing or what can be calculated for the moment ie.
all prerequisits for starting Qsmr calculations are resolved. Hermod also
serves other automated systems like IASCO model with data.

.. .. _Python: http://python.org


Required dependencies - Installation and configuration
======================================================

The Odin processing chain and Hermo make use of third party software.
They are all based on some type of open source license like GNU GPL or BSD
license.

Hermod is buildt to run on Ubuntu Linux 10.04 (server version) but may work on
different Ubuntu versions aswell as other POSIX OS:es probably even on windows.

Hermod needs other components to work properly:

Python_ :

        Hermods core is implemented in Python 2.6. But other versions may also
        work.

MySQL_ :

        Relational database to manage metadata. Database installation for this
        project i discussed in `Installation of the Database`_

Torque_ :

        Torque is a Cluster Resource Manager.  Documentation and detailed
        installation instructions can be found at Torque_ documentation pages.
        Site specific configuration will be discussed in `Torque
        configuration`_ section.

Maui_ :
        
        The Cluster Scheduler only site specific setup vill be noted in `Maui
        configuration`_

Other tools :
        
        GCC have to be installed to be able to compile all python modules.

.. _Python: http://python.org/
.. _MySQL: http://dev.mysql.com/doc/refman/5.1/en/
.. _Torque: http://www.clusterresources.com/products/torque/docs
.. _Maui: http://www.clusterresources.com/products/maui/docs

 
Installation of the Database
-----------------------------
 
Configuration of database is minimal. Standard apt installation of the package
mysql-server is enough see `Appendix A - MySQL create script`_ and `Appendix B
- MySQL Table layout`_ for database and table layout.

Torque configuration
--------------------
 
Two types of Torque installations are required - one server installation and
several client installations on each node in the cluster. The server
installation manages the queueingsystem and needs to know about all clients
(computee nodes) in the cluster. The clients does only need to know about the
server.

 
Torque client configuration
___________________________
 
A site-specific installation script
``/misc/apps/torque-package-mom-linux-x86_64.sh`` provided all configuration
needed at the client. But some additional configuration is needed to provide
the per session temp directory.

The following script makes all steps in the installation process.

.. code-block:: txt

        #!/bin/bash
        # A script to install, prepare and start a node
        # run as root

        aptitude purge torque-mom torque-client -y
        sh /misc/apps/torque-package-mom-linux-x86_64.sh --install
        cp /misc/apps/prologue.user /var/spool/torque/mom_priv/
        cp /misc/apps/epilogue.user /var/spool/torque/mom_priv/
        ldconfig
        pbs_mom

An important part of the processing system is the scripts at the client that
creates a temporary directories before a processing starts and removes it when
processing is finished. These scripts runs wether or not the processing was
successful or not.

Torque server configuration
___________________________
 
A site-specific installation script ``torque-package-server-linux-x86_64.sh``
installs binaries and libraries and some basic configuration. Editing
configuration files to reflect connected nodes and their capabilities is
necesary.

The file ``/var/spool/torque/server_priv/nodes`` defines the computee nodes:

.. code-block:: txt

        glass np=8 hermod node x86_64
        sard np=2 hermod node x86_64 
        ...

The attributes hermod, node and x86_64 specifies different capabilities en each
node. 'x86_64' tells us the architechture on the node is 64 bits. 'hermod'
states that hermod, Qsmr and Q-pack in installed and works correctly. The last
attribute shows us the computer is a node with no other users than the torque
queue operates the computer. 'desktop' would state it is a workstation with
human users.

Some additional settings con be done through torque's configuration program
``qmgr``. A printout of Torque server settings generated with ``qmgr -C 'print
server'`` can be found in `Appendix C - Torque server settings`_.

Torque starting and stopping
____________________________

There are currently no system V init scripts implemented. Starting and stopping
server and nodes is manual. There is no problem shutting off a node before the
server but the running job at the node will be killed. If server is stopped the
current queue will be saved and the current running jobs at the moms will
continue. When server is started again moms will report their finished jobs. 

start server at morion:

.. code-block:: txt

        $ /usr/local/sbin/pbs_server

start moms at nodes:

.. code-block:: txt

        $ /usr/local/sbin/pbs_mom

stop moms at nodes:

.. code-block:: txt

        $ /usr/local/sbin/momctl -s

stop server at morion:

.. code-block:: txt

        $ /usr/local/bin/qterm -t immediate

 
Maui configuration
------------------
 
The main configuration file can be found at ``morion.rss.chalmers.se``.
 
         /usr/local/maui/maui.cfg
 
         
Full configuration file can be found in `Appendix D - Maui configuration`_.
This setup restrict one user to take all resources at once enforcing Odin
processing always have atleast a minimum of processer available but also giving
users acccess to the queue.

start the scheduler:

.. code-block:: txt

        $ /usr/local/bin/maui

stop the scheduler:

.. code-block:: txt

        $ /usr/local/maui/bin/schedctl -k


HERMOD
======

Overview
--------

Hermod is a program suite written in Python that wraps around QSMR and inserts
metadata in to the SMR database. Hermod runs regulary and decides when to run
QSMR according to information Hermod can find in the SMR Database. Hermod
provides a fully automatic processing system for processing data from Level1
data to Level2 data.

Package details
---------------

Hermod is divided into several smaller enteties that provide specific
functionality. The current status of the source code is still in a form of
transistion from one package to more and smaller sub packages.

odin.hermod

The odin.hermod package is the package which is responsible for the infomation
and bookkeeping parts of hermod i.e keep track of file transactions,
filedependencies and finally submitting jobs to the queueing system


odin.config

The odin.config i more or less a configuration package Hermod and Iasco shares
this package

HERMOD Installation
-------------------

For the moment hermod is running from the development source i.e. from the
directory ``~odinop/hermod_jm`` for ubuntu 10.04 and  ``~odinop/hermod_glass``
for 9.08 this directory is checked out from svn. This is not by any mean the
ideal way to maintain a piece of software. This is a temporary solution.

Best way to continue development is to separate development and production.
First all processing nodes and servers in the system need to have the same OS
version (ubuntu 10.04 LTS). Using the same OS makes it possible to run Hermod
from on single installation shared by NFS.

Hermod packages already exits in ``/misc/apps/odinsite`` a simple buildout
installation.

.. code-block:: txt

        [buildout]
        parts = 
                odin
        find-links =
                /misc/apps/odinsite
        
        [odin]
        recipe = zc.recipe.egg
        interpreter = odinpy
        eggs = 
                odin.config
                odin.iasco
                odin.hermod
                mocker
                pymatlab
                fuse-python
                numpy
                scipy
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

Developers installation
_______________________

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

The source of  hermod is available at `Chalmers' Subversion repoitory`__ .

.. _svn: http://svn.rss.chalmers.se/svn/odinsmr/hermod

__ svn_

Datamodel
---------

The database consists of a number of loosly connected tables with records
(rows) describing meta data about satelite measurement or file stored on disk.

The Hermod data model is pretty simple. All tables are 'nitted' together with a
'id' field. For example in the 'level1'-table the logical key that identifies
each row is the fields 'orbit','calversion' and 'freqmode'.

level1:
        
.. code-block:: txt

        id -> orbit, calversion, freqmode -> 'records in level1'

The 'id'-field is included in the 'level2'-table to make it possible to find all level2 products derived from a 'level1' record.

level2:
        
.. code-block:: txt

        id, fqid, scanno -> 'records in level2-table'

level2files:
        
.. code-block:: txt

        id, fqid -> 'records in level2files-table'


Finding scans available for processing
______________________________________

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

Queuing and execution
_____________________

.. A "job" is defined from the lookup in the previous section. And information
.. about the processing is sent to a queue for later execution. The Resource
.. system that handles the queue and the execution nodes in the computing cluster
.. (``smiles-p3``, ``smiles-p4``, ``smiles-p5,...``) is Torque_. 
.. Basically the "job" is a shell script sent to another machine for execution.
.. 
.. The script ``launchjobs`` described in juno.pbs_ puts  the script ``junorunner`` in queue with different input parameters to  run on the computee nodes.

Processing
__________

The ``hermodprocessor``-script executes the main-function in
``odin.hermod.processor``-module. This module looks in the database to find
level1b records which not have as many corresponding level2 records as hermod
expects.

When Hermod detects a job to run - Hermod sends a wrapped Qsmr job to the
processing cluser and collects the results and puts them in the dabase and the
filesystem.


Appendix A - MySQL Create script
================================

.. This script is available at the SMILES svn-repository_
.. 
.. .. _svn-repository: http://svn.rss.chalmers.se/svn/smiles/branches/jmbranch2/docs/database_model.sql

Appendix B - MySQL Table layout
===============================

.. .. image:: database_model.png
 
Appendix C - Torque server settings
===================================

.. code-block:: txt

        #
        # Create queues and set their attributes.
        #
        #
        # Create and define queue batch
        #
        create queue batch
        set queue batch queue_type = Execution
        set queue batch resources_default.nodes = 1
        set queue batch resources_default.walltime = 01:00:00
        set queue batch enabled = True
        set queue batch started = True
        #
        # Create and define queue new
        #
        create queue new
        set queue new queue_type = Execution
        set queue new resources_default.nodes = 1
        set queue new resources_default.walltime = 01:00:00
        set queue new enabled = True
        set queue new started = True
        #
        # Create and define queue new
        #
        create queue rerun
        set queue rerun queue_type = Execution
        set queue rerun resources_default.nodes = 1
        set queue rerun resources_default.walltime = 01:00:00
        set queue rerun enabled = True
        set queue rerun started = True
        #
        # Set server attributes.
        #
        set server scheduling = True
        set server acl_hosts = morion
        set server managers = root@morion.rss.chalmers.se
        set server operators = root@morion.rss.chalmers.se
        set server default_queue = batch
        set server log_events = 511
        set server mail_from = adm
        set server query_other_jobs = True
        set server scheduler_iteration = 600
        set server node_check_rate = 150
        set server tcp_timeout = 6
        set server mom_job_sync = True
        set server keep_completed = 300
        set server auto_node_np = True
        set server next_job_number = 18315

Appendix D - Maui configuration
===============================
 
The only configuration file is in /usr/local/maui/maui.cfg:

.. code-block:: txt
        
        # maui.cfg 3.3
        
        SERVERHOST            morion
        # primary admin must be first in list
        ADMIN1                root e0joakim jo
        ADMIN2		      donal odinop
        ADMIN3		      all
        
        # Resource Manager Definition
        
        RMCFG[base] TYPE=PBS
        
        # Allocation Manager Definition
        
        AMCFG[bank]  TYPE=NONE
        
        # full parameter docs at http://supercluster.org/mauidocs/a.fparameters.html
        # use the 'schedctl -l' command to display current configuration
        
        RMPOLLINTERVAL        00:00:30
        
        SERVERPORT            42559
        SERVERMODE            NORMAL
        
        # Admin: http://supercluster.org/mauidocs/a.esecurity.html
        
        
        LOGFILE               maui.log
        LOGFILEMAXSIZE        10000000
        LOGLEVEL              3
        
        # Job Priority: http://supercluster.org/mauidocs/5.1jobprioritization.html
        
        QUEUETIMEWEIGHT       1 
        
        # FairShare: http://supercluster.org/mauidocs/6.3fairshare.html
        
        FSPOLICY              PSDEDICATED
        FSDEPTH               7
        FSINTERVAL            6:00:00
        FSDECAY               0.80
        
        FSWEIGHT 10
        CREDWEIGHT 100
        USERWEIGHT 0
        GROUPWEIGHT 0
        CLASSWEIGHT 100
        SERVICEWEIGHT 1
        QUEUETIMEWEIGHT 1
        FSCLASSWEIGHT 100
        FSUSERWEIGHT 0
        
        
        # Throttling Policies: http://supercluster.org/mauidocs/6.2throttlingpolicies.html
        
        # NONE SPECIFIED
        
        # Backfill: http://supercluster.org/mauidocs/8.2backfill.html
        
        BACKFILLPOLICY        FIRSTFIT
        RESERVATIONPOLICY     CURRENTHIGHEST
        
        # Node Allocation: http://supercluster.org/mauidocs/5.2nodeallocation.html
        
        NODEALLOCATIONPOLICY  MINRESOURCE
        
        # QOS: http://supercluster.org/mauidocs/7.3qos.html
        
        # QOSCFG[hi]  PRIORITY=100 XFTARGET=100 FLAGS=PREEMPTOR:IGNMAXJOB
        # QOSCFG[low] PRIORITY=-1000 FLAGS=PREEMPTEE
        
        # Standing Reservations: http://supercluster.org/mauidocs/7.1.3standingreservations.html
        
        # SRSTARTTIME[test] 8:00:00
        # SRENDTIME[test]   17:00:00
        # SRDAYS[test]      MON TUE WED THU FRI
        # SRTASKCOUNT[test] 20
        # SRMAXTIME[test]   0:30:00
        
        # Creds: http://supercluster.org/mauidocs/6.1fairnessoverview.html
        
        USERCFG[DEFAULT]      FSTARGET=20 MAXJOB=10
        USERCFG[odinop]       FSTARGET=50 MAXJOB=50
        # USERCFG[john]         PRIORITY=100  FSTARGET=10.0-
        # GROUPCFG[staff]       PRIORITY=1000 QLIST=hi:low QDEF=hi
        #CLASSCFG[batch]       FLAGS=PREEMPTEE
        CLASSCFG[batch]       FLAGS=PREEMPTEE PRIORITY=10000
        # CLASSCFG[interactive] FLAGS=PREEMPTOR
        CLASSCFG[batch] FSTARGET=40.0
        CLASSCFG[rerun] FSTARGET=20.0
        CLASSCFG[new] FSTARGET=40.0
        
