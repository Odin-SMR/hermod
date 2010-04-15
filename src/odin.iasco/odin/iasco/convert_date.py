#!/usr/bin/python

'''
This is a date converter that convert Modified Julian Dates to Coordinated Universal Time and vice versa. The code is more or less copied and adapted from the matlab scripts mjd2utc.m and utc2mjd.m.

Written by Erik Zakrisson 2008-10-07 (or 54746)
'''

import numpy as n
from matplotlib import mlab as m

def mjd2utc(mjd):
	'''mjd2utc(mjd)
	Input mjd as int
	'''
	dayfrac = mjd - n.floor(mjd)
	jd      = n.floor(mjd) + 2400000.5;
	jd0     = jd+0.5;

	if jd0 < 2299161.0:			# Determine the calendar
		c = jd0 + 1524.0        # Its Julian
	else:                      # Its Gregorian.
		b = n.fix(((jd0 - 1867216.25) / 36524.25))
		c = jd0 + (b - n.fix(b/4)) + 1525.0

	d     = n.fix( ((c - 122.1) / 365.25) )
	e     = 365.0 * d + n.fix(d/4)
	f     = n.fix( ((c - e) / 30.6001) )
	day   = n.fix( (c - e + 0.5) - n.fix(30.6001 * f) )
	month = n.fix( (f - 1 - 12*n.fix(f/14)) )
	year  = n.fix( ( d - 4715 - n.fix((7+month)/10)) )
	hour     = n.fix(dayfrac*24.0)
	minute   = n.fix(dayfrac*1440.0%60.0)
	dayfrac  = dayfrac * 86400.0
	ticks    = dayfrac%60.0
	secs     = n.fix(ticks)
	ticks    = ticks - secs
	seconds  = secs + ticks

	return int(year), int(month), int(day), int(hour), int(minute), int(secs), int(ticks)

def utc2mjd(*args): 
	'''utc2mjd(*args)
	Input (args) at the form YYYY,MM,DD(,HH,MM,SS,TT)
	'''
	year,month,day=args[0],args[1],args[2]

	if n.size(args) < 4:
		hour  = 0
	else:
		hour  = args[3]

	if n.size(args) < 5:
		minute = 0
	else:
		minute  = args[4]

	if n.size(args) < 6:
		secs   = 0
	else:
		secs  = args[5]

	if n.size(args) < 7:
		ticks  = 0
	else:
		ticks  = args[6]

	I=m.find(year<100)
	if n.size(I)!=0:
		subset=year
		J=m.find(subset>40)
		subset=subset+2000
		if n.size(J)!=0:
  			subset=subset-2000+1900
		year=subset

	y = n.fix(year)
   
	I=m.find(month<=2)
	if n.size(I)!=0:
		y=y-1
		month=month+12

	if ((year < 1582) | ((year == 1582) & ((month < 10) | ((month == 10) & (day < 15)))) ):
		B = n.fix(-2 + n.fix((y+4716)/4) - 1179)
	else:
		B = n.fix(y/400) - n.fix(y/100)+ n.fix(y/4)

	A = 365.0*y - 679004.0
	mjd =  A+B+(n.fix(30.6001*(month+1)))+day+(hour/24.0)+minute/1440.0+(secs+ticks)/86400.0
	
	return int(mjd) # NB! Delete the int command to get the mjd as a double
