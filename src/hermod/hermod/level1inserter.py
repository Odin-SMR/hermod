"""
Level1 inserter

inserts level1file into hermod db
"""
from os import walk
from os.path import getctime
from os.path import join as path_join
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from hermod.model import HdfFile, LogFile, Scan, Level1
from datetime import datetime
from sys import argv
import re

class FileServer(object):
    """ Handles Odin files in a directory
    """
    def __init__(self, path):
        self.path = path

    def add_files(self):
        """ a list of all files in the storage
        """
        file_list = []
        for dirpath, _, fnames in walk(self.path):
            for filename in fnames:
                file_list.append(path_join(dirpath, filename))
        return file_list

class Level1Inserter(object):
    def __init__(self, level1b_dir):
        engine = create_engine('mysql://odinuser:***REMOVED***@mysqlhost/hermod')
        session = sessionmaker(bind=engine)
        self.ses = session()
        self.pattern = re.compile(
            "^.*(?P<calversion>[\d]+\.[\d]+).*"
            "O(?P<backend>[ABCD])"
            "1B(?P<orbit>[\w]{4,5})"
            "\.(?P<type>[\w]{3})"
            "(?:$|\.gz$)"
        )
        file_storage = FileServer(level1b_dir)
        file_list = file_storage.add_files()
        for l1_file in file_list:
            match = self.pattern.search(l1_file)
            if match is None:
                continue
            matchdict = match.groupdict()
            backend = matchdict['backend']
            file_type = matchdict['type']
            calversion = matchdict['calversion']
            orbit = eval("0x" + matchdict['orbit'])
            logfile = []
            hdffile = []
            if file_type == "HDF":
                hdffile = [HdfFile(
                    filedate=datetime.fromtimestamp(getctime(l1_file)),
                    update=datetime.now()
                    )]
            if file_type == "LOG":
                logfile = [LogFile(
                    filedate=datetime.fromtimestamp(getctime(l1_file)),
                    update=datetime.now())]
            level1 = self.ses.query(Level1).filter_by(
                orbit=orbit,
                calversion=calversion,
                backend=backend,
                ).first()
            if level1:
                if file_type == "HDF":
                    level1.hdffile = hdffile
                if file_type == "LOG":
                    level1.logfile = logfile
            else:
                self.ses.add(
                    Level1(
                        orbit=orbit,
                        calversion=calversion,
                        backend=backend,
                        logfile=logfile,
                        hdffile=hdffile,
                        )
                    )
            self.ses.commit()

def main():
    """IT all starts here"""
    if len(argv) == 1:
        level1b_dirs = ['/odin/smr/Data/level1b/']
    else:
        level1b_dirs = argv[1:]
    for level1b_dir in level1b_dirs:
        Level1Inserter(level1b_dir)


if __name__ == '__main__':
    main()
