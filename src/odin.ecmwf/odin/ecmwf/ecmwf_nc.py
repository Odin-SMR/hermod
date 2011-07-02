#!/usr/bin/env python


from tempfile import NamedTemporaryFile
from subprocess import Popen
from ctypes import CDLL
import os, string, sys, glob

class Ecmwf_Grib2(object):
    def __init__(self,grib_filename):
        self.filename = grib_filename
	self.nc_file = NamedTemporaryFile()

    def convert2nc(self):
        session = Popen(['cdo','-f nc4','-R','-q','-t ecmwf','copy',
                self.filename, self.nc_file.name])
        exit_code = session.wait()
        if exit_code<>0:
            self.nc_file.close()
            raise RuntimeError('Exitcode from cdo: {0}'.format(exit_code))

    def outfile(self):
	return 'test_nc.nc'

    def convert2odin(self):
	odin_nc = CDLL('./lib/odinp_grib2.so.1.0.0')
	odin_nc.create_odin_nc(self.nc_file.name,self.outfile())
