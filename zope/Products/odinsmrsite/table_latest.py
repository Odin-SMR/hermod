#!/usr/bin/python
#
#	table_latest.py
#
#	Glenn Persson, Dec. 2007
#
#	Show latest orbits and processed dates for level0/level1/level2
# 	Purpose: to be used as a status information portlet
#
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import UniqueObject,SimpleItemWithProperties
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from hermod.hermodBase import *
from sys import exit,stderr
from optparse import OptionParser
from os import environ
import MySQLdb
import string

from config import *
class tablelast(UniqueObject,SimpleItemWithProperties):

  meta_type = 'GlennTools'
  id = 'table_latest'
  security = ClassSecurityInfo()


  def tlast(self,table):

    # Initiate a database connection
    try:
        db = MySQLdb.connect(host=config.get('READ_SQL','host'), user=config.get('READ_SQL','user'), db='smr')
    except Warning,inst:
        print >> stderr, "Warning: %s" % inst

    if table == 'level0':
    	query = 'select max(stop_orbit) as c from level0'
    elif table == 'level1':
    	query = 'select max(orbit) as c from level1'
    elif table == 'level2':
    	query = 'SELECT max(orbit) as c FROM level1 JOIN level2files ON (level2files.id = level1.id)'


    #  do the query
    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    try:
    	status = cursor.execute(query)
    except StandardError,e:
        print >> stderr, "Hermod:", str(e)
        exit(3)
    except Warning,e:
        print >> stderr, "Hermod:", str(e)
    except KeyboardInterupt:
        print >> stderr, "Hermod: KeyboardInterrupt, closing database..."
        cursor.close()
        db.close()

    if status == 0: 
    	exit(0)

    n = cursor.fetchone()

    cursor.close()
    db.close()
       
    buf = n["c"]
    orbit = int(round(buf))
    hex_buf = string.upper(hex(orbit))[2:]
    hex_string = hex_buf
    while (len(hex_string) < 4):
            hex_string = "0"+hex_string
    result = str(orbit) + " (0x" + hex_string + ")"

    return result
