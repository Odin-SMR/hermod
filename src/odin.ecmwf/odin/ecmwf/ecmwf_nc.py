#!/usr/bin/env python

from tempfile import NamedTemporaryFile
from subprocess import Popen,PIPE
from StringIO import StringIO
from datetime import datetime
from ctypes import CDLL
import os, string, sys, glob
from  pkg_resources import resource_filename
from shutil import copy
from os import mkdir
from odin.config.environment import config
from os.path import dirname,isdir,split,join

def makedir(dirname):
    '''Makes the directories to ensure the path to filename exists.
    '''
    if not isdir(dirname):
        makedir(split(dirname)[0])
        mkdir(dirname)
    else:
        return

class Ecmwf_Grib2(object):
    def __init__(self,grib_filename):
        self.filename = grib_filename
        self.time = datetime.strptime(self.filename,'ECMWF_ODIN_%Y%m%d%H%M+000H00M')
	self.nc_file = NamedTemporaryFile()
        self.an_file = NamedTemporaryFile()

    def convert2nc(self):
        err = StringIO()
        out = StringIO()
        session = Popen(['cdo','-f nc4','-t ecmwf','copy',
                self.filename, self.nc_file.name])#,stdout=PIPE,stderr=PIPE)
        exit_code = session.wait()
        if exit_code<>0:
            raise RuntimeError('Exitcode from cdo: {0}\nmessage: {1}'.format(
                    exit_code,'message'))

    def outfile(self):
	conf = config()
        basepath = conf.get('ecmwf','basedir')
        fullpath = join(basepath,'%Y','%m','ODIN_NWP_%Y_%m_%d%H_%M_00_00_'
                + str(self.nlev)+'_AN.NC')
                
	return self.time.strftime(fullpath)

    def convert2odin(self):
        odinp_lib = resource_filename('odin.ecmwf',
                'odinecmwf/odinp_grib2.so.1.0.0')
	odin_nc = CDLL(odinp_lib)
	self.nlev = odin_nc.create_odin_nc(self.nc_file.name,self.an_file.name)

    def cpfile(self):
        makedir(dirname(self.outfile()))
        copy(self.an_file.name,self.outfile())


