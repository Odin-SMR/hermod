#!/usr/bin/env python


from tempfile import NamedTemporaryFile
from subprocess import Popen
import os, string, sys, glob

class Ecmwf_Grib2(object):
    def __init__(self,grib_filename):
	self.nc_file = NamedTemporaryFile()

    def convert2nc(self)
        session = Popen(['cdo','-fnc4','-R','-q','-tecmwf','copy',filename,
                self.nc_file])
        exit_code = session.wait()
        if exit_code<>0:
            self.nc_file.close()
            raise RuntimeError('Exitcode from cdo: {0}'.format(exit_code))

    def convert2odin(self):
        session = Popen(['/odin/external/ecmwfNCD/OPINP',self.nc_file])
        exit_code = session.wait()
        if exit_code==0:
            
            self.nc_file.close()

    
    

def convert2Odin(self):
    grib = glob.glob("ECMWF_ODIN*M")
    if (len(grib) == 0):
        sys.exit(0)

for nfile in nc:
    print "%d/%d %s" % (count,len(nfile),nfile)
    cmd = "%s %s" % ("/odin/external/ecmwfNCD/ODINP",nfile)
    print cmd
    os.system(cmd)
    os.remove(nfile)
    count += 1
print "Completed processsing file(s)"
