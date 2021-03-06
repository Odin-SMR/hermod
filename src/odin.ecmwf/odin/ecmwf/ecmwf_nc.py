#!/usr/bin/env python

from tempfile import NamedTemporaryFile
from subprocess import Popen, PIPE
from datetime import datetime
from ctypes import CDLL
from pkg_resources import resource_filename
from shutil import copy, move
from os import mkdir, chmod
from odin.config.environment import config
from os.path import dirname, isdir, split, join, basename, exists
import logging


def makedir(dirname):
    '''Makes the directories to ensure the path to filename exists.
    '''
    if not isdir(dirname):
        makedir(split(dirname)[0])
        mkdir(dirname)
        # log.info('Creating new directory {0}'.format(dirname))
    else:
        return


class Ecmwf_Grib2(object):
    def __init__(self, grib_filename):
        self.log = logging.getLogger(__name__)
        self.filename = grib_filename
        self.time = datetime.strptime(basename(self.filename),
                                      'ECMWF_ODIN_%Y%m%d%H%M+000H00M')
        self.nc_file = NamedTemporaryFile()
        self.an_file = NamedTemporaryFile()
        self.conf = config()

    def convert2nc(self):
        session = Popen(['cdo', '-f', 'nc4', '-t', 'ecmwf', 'copy',
                        self.filename, self.nc_file.name], stdout=PIPE,
                        stderr=PIPE)
        exit_code = session.wait()
        if exit_code != 0:
            message = session.stderr.read()
            self.log.critical(
                'cdo fails with exitcode {0} and error message {1}'.format(
                    exit_code, message))
            raise RuntimeError('Exitcode from cdo: {0}\nmessage: {1}'.format(
                exit_code, message))
        self.log.debug(
            'cdo executed with exitcode: {0} and message {1}'.format(
                exit_code, session.stdout.read()))

    def outfile(self):
        basepath = self.conf.get('ecmwf', 'basedir')
        fullpath = join(basepath, '%Y', '%m', 'ODIN_NWP_%Y_%m_%d_%H.NC')

        return self.time.strftime(fullpath)

    def delete(self):
        target_file = basename(self.filename)
        target_dir = self.conf.get('ecmwf', 'trash')
        move(self.filename, join(target_dir, target_file))
        self.log.debug('Moved {0} to trashdir: {1}'.format(target_file,
                                                           target_dir))

    def convert2odin(self):
        odinp_lib = resource_filename('odin.ecmwf',
                                      'odinecmwf/odinecmwf_grib2.so')
        if not exists(odinp_lib):
            self.log.critical('odinecmwf_grib2.so not installed')
            exit(1)
        odin_nc = CDLL(odinp_lib, mode=1)
        self.log.debug('Starting create_odin_nc  {0}'.format(
            self.nc_file.name))
        status = odin_nc.create_odin_nc(self.nc_file.name, self.an_file.name)
        if status == -1:
            self.log.error(
                'Error while creating odin_nc files from {0}'.format(
                    self.filename))
            raise RuntimeError(
                "Somefields might be missing in file {0}".format(
                    self.filename))
        self.log.debug('create_odin_nc completed')

    def cpfile(self):
        makedir(dirname(self.outfile()))
        copy(self.an_file.name, self.outfile())
        chmod(self.outfile(), 0o644)
        self.log.debug('Installed {0}'.format(self.outfile()))
