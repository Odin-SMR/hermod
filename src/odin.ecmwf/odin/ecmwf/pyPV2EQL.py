#! /usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------

'''
created on 20 Feb 2012
@Author Kazutoshi Sagi

calculate EQL (EQivarent Latitudes) from netcdf file.
The netcdf file generally can be found in directory "/odin/external/ecmwfNCD".

This function is based on matlab routine.
The Original routine is in odintools/ecmwf.
'''

usage = "pyPV2EQL.py [options] file"
__version__ = "0.1"
__filename__ = "pyPV2EQL.py"
__user__ = 'odinop' #operator

#------------------------------------------------------------------

import numpy as np
import odin.ecmwf.eqltools.calc_eql as CE
import time,datetime,sys,os,pwd
from optparse import OptionParser

#------------------------------------------------------------------

def utc2mjd(*args):
	'''
	utc2mjd(year, month, day[, hour[, minute[, second[, microsecond[,tzinfo]]]]])
	return MJD value
	'''
	t = datetime.datetime(*args)
	tj = datetime.datetime(1858,11,17,0,0,0) # reference date for MJD
	dtj = t - tj
	return dtj.days + dtj.seconds/86400.

def mjd2utc(mjd):
	'''
	mjd2utc(mjd)
	return UTC tuple (year, month, day, hour, minut, second)
	'''
	te = datetime.datetime(1970,1,1,0,0) # reference date for epoch
	tj = datetime.datetime(1858,11,17,0,0,0) # reference date for MJD
	dje = te - tj
	dje_sec = dje.days*86400. + dje.seconds
	mjd_sec = mjd*86400.
	return time.gmtime(mjd_sec-dje_sec)[:6]

def main(filename,force=False):
	'''
	main process to convert netcdf file to matlab file
	
	Example
	----------
	main('/odin/external/~~~~~~~~~~~~~.NC',True)
	matlab file must be created in same directory with NC file
        '''
	#check usee name
	if (pwd.getpwuid(os.getuid())[0]!=__user__) & (pwd.getpwuid(os.getuid())[0]!='root'):
		msg = 'Error '+__filename__+': to be run by user odinop or root! you are %s'%(pwd.getpwuid(os.getuid())[0])
	        raise RuntimeError,msg

	#load netcdf file
	pv_ext = '.lait.mat' # PV converted to scaled pv according to Lait!!

	# file names
	inputfile = filename	
	outputfile = filename.replace('.NC',pv_ext)

	# load
	if not os.path.isfile(inputfile):
		msg = 'Warning '+__filename__+': no %s exists!!'%inputfile
		raise RuntimeError,msg
	else:
		if np.logical_and(os.path.isfile(outputfile),force==False): #check existance of file and force writting flag
			msg = 'Warning '+__filename__+': %s exists already, skipped'%outputfile
			raise RuntimeError,msg
		else:
			d = CE.EQL(inputfile) #load data
			d.get_eql() #calculate

			#write file
			d.saveasmat(outputfile)


#------------------------------------------------------------------

if __name__ == '__main__':
	parser = OptionParser(usage=usage, version=__filename__+' '+__version__)
	
	parser.add_option("-F", "--force", dest="force",
					  help="force writing existing mat files", metavar="bool", default=False)

	(options, args) = parser.parse_args()
	
	print(options,args)

	if len(args) != 1:
		raise IOError,'filename should have been as Input'
	else:
                filename = args[0]
		main(filename,force=options.force)
