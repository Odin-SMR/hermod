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

usage = "pyPV2EQL.py [options] startmjd stopmjd"
__version__ = "0.1"
__filename__ = "pyPV2EQL.py"
__user__ = 'odinop' #operator

file_format = 'ODIN_NWP_YYYY_MM_DD_HH'

#------------------------------------------------------------------

import numpy as np
import tools.calc_eql as CE
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

def main(datetimeobj,path,force=False):
	'''
	main process to convert netcdf file to matlab file
	
	Example
	----------
	main('2001-01-01 00:00','./',True)
	'''
	#check usee name
	if (pwd.getpwuid(os.getuid())[0]!=__user__) & (pwd.getpwuid(os.getuid())[0]!='root'):
		print('Error '+__filename__+': to be run by user odinop or root!')
		print(pwd.getpwuid(os.getuid())[0])
		return

	#load netcdf file
	pv_type = '.lait' # PV converted to scaled pv according to Lait!!

	yy = datetimeobj.year
	mm = datetimeobj.month
	dd = datetimeobj.day
	hh = datetimeobj.hour
	
	# file names
	dirpath = path+'/%04i/%02i/'%(yy,mm)
	filename = dirpath+file_format.replace('YYYY','%04i'%yy).replace('MM','%02i'%mm).replace('DD','%02i'%dd).replace('HH','%02i'%hh)

	inputfile = filename+'.NC'	
	outputfile = filename+pv_type+'.mat'

	# load
	if not os.path.isfile(inputfile):
		print('Warning '+__filename__+': no %s exists!!'%inputfile)
		return
	else:
		if np.logical_and(os.path.isfile(outputfile),force==False): #check existance of file and force writting flag
			print('Warning '+__filename__+': %s exists already, skipped'%outputfile)
			return
		else:
			print('... processing ...')
			print('%s --> %s'%(inputfile,outputfile))
			d = CE.EQL(inputfile) #load data
			d.get_eql() #calculate

			#make directories (includes intermidiates)
			if not os.path.isdir(os.path.dirname(outputfile)):os.makedirs(os.path.dirname(outputfile))
			#write file
			d.saveasmat(outputfile)
			print('data saved into %s'%outputfile)


#------------------------------------------------------------------

if __name__ == '__main__':
	parser = OptionParser(usage=usage, version=__filename__+' '+__version__)
	
	parser.add_option("-F", "--force", dest="force",
					  help="force writing existing mat files", metavar="bool", default=False)
	parser.add_option("--path", dest="path",default='/odin/external/ecmwfNCD',
					  help="base path of pv file directory. default is '/odin/external/ecmwfNCD'")

	(options, args) = parser.parse_args()
	
	print(options,args)

	if len(args) != 1:
		raise IOError,'have to put 4 values (yyyy,mm,dd,hh) for Input'
	else:
		args = np.asarray(args,dtype=np.int)
		datetimeobj = datetime.datetime(*args)
		main(datetimeobj,options.opath,force=options.force)
