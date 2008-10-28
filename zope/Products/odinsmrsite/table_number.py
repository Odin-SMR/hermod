#!/usr/bin/python
#
#	table_number.py
#
#	Glenn Persson, Nov. 2007
#
# 	Show number of rows for tables: level0, level1 and level2
#	Purpose: to be used as a status information portlet 
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

from config import *
class tablenums(UniqueObject,SimpleItemWithProperties):

  meta_type = 'GlennTools'
  id = 'table_number'
  security = ClassSecurityInfo()


  def tnums(self,table):

    # Initiate a database connection
    try:
        db = MySQLdb.connect(host=config.get('READ_SQL','host'), user=config.get('READ_SQL','user'), db='smr')
    except Warning,inst:
        print >> stderr, "Warning: %s" % inst

    if table == 'level0':
    	query = 'select count(*) from level0'
    elif table == 'level1':
    	query = 'select count(*) from level1'
    elif table == 'level2':
    	query = 'select count(*) from level2files'


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
         
    return n["count(*)"]
