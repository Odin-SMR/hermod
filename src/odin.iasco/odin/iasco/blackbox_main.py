#!/usr/bin/python
# coding: UTF-8

""" 
    This main program controls all the parts needed to produce pictures of assimilated fields of the tracer gases O3, HNO3, H2O and N2O. 
    For more information about the different parts, please see each program and the associated README.txt file.
"""

from datetime import date as dtdate
from datetime import timedelta
from winds import extractWinds, copyWinds
from tracer_fields import hdfRead
from assimilation import assimilate
from pics import makePictures
from subprocess import Popen,PIPE
from sys import stdout,stderr
from db_calls import *
import sys
import logging
import logging.config
from odin.config.environment import config
from pkg_resources import resource_filename, resource_stream

def main():
    
    name = config().get('logging','configfile')
    file = resource_stream('odin.config',name)
    logging.config.fileConfig(file)
    root_logger = logging.getLogger("")
    logger = logging.getLogger("iasco")
  
    zope = Popen(['/usr/local/Plone/zinstance/bin/zopepy',resource_filename('odin.iasco','addlevel3.py')],stdin=PIPE,stdout=stdout,stderr=stderr)
    new_dates=getNewDates()
    start_date=getStartDate()

    if start_date:
        if new_dates:
            dates=[start_date]
            i=0
            while not dates[i]==new_dates[-1]:
                dates.append(dates[i]+timedelta(1))
                i=i+1
        else:
            dates=[start_date]
            i=0
            while not dates[i]==dtdate.today():
                dates.append(dates[i]+timedelta(1))
                i=i+1
    else:
        dates=new_dates
    
    runNo=0
    for date in dates:
        for fqid in [3,29]:
            if fqid==3:
                version='2-0'
            elif fqid==29:
                version='2-1'
        
            wind=getWindBool(date,fqid)
            if wind: windstr = 'wind processes'
            else: windstr = ''
            hdf=getHdfBool(date,fqid)
            if hdf: hdfstr = 'tracer fields processes'
            else: hdfstr = ''
            assim=getAssimilateBool(date,fqid)
            if assim: assimstr = 'assimilation processes'
            else: assimstr = ''
            logger.info('The process started for date:',str(date),'and fqid:',fqid,'for',windstr,hdfstr,assimstr)
            
            if wind:
                if fqid==3: # The wind extraction is not needed for both fqid
                    extractWinds(date)
                assimilate(date-timedelta(1),fqid)
                makePictures(date-timedelta(1),fqid,zope)
                w2iasco(date-timedelta(1),fqid,version)
                runNo=runNo+1
            if date in new_dates and fqid==3: # The wind extraction is not needed for both fqid
                extractWinds(date+timedelta(1))
            if hdf:
                orbit_list=getOrbitInfo(date,fqid,version)
                hdfRead(date,orbit_list,fqid)
            if assim or wind or hdf or (date in new_dates):    
                if fqid==3: # The wind extraction is not needed for both fqid
                    copyWinds(date)
                    copyWinds(date+timedelta(1))
                assimilate(date,fqid)
                makePictures(date,fqid,zope)
                w2iasco(date,fqid,version)
                
                if hdf:
                    assids=getAssid(date,fqid)
                    for assid in assids:
                        w2iasco_orbits(date,assid,orbit_list['l1id'])
                
                logger.info('The process is complete for date:',date,'and fqid:',fqid)
                runNo=runNo+1
        
        if runNo>=15:
            break
    zope.stdin.close()
    zope.wait()
    sys.exit(0)
