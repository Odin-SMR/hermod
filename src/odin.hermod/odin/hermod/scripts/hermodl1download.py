#!/usr/bin/python
"""Download level1 files from PDC
"""

from sys import stderr
from optparse import OptionParser
from datetime import datetime,timedelta
from time import strptime,mktime
from odin.hermod.level1 import findids
from odin.hermod.hermodBase import config


def parsetime(option,opt_str,value,parser):
    '''Parse time string in YYYYMMDD HH:MM format to time.

    optparse callback function.
    '''
    try:
        t = datetime.fromtimestamp(mktime(strptime('%s %s' % value,'%Y%m%d %H:%M')))
    except ValueError:
        parser.error('Please type date according to ISO 8601 YYYYMMDD HH:MM')
    setattr(parser.values,option.dest,t)

def hex2dec(option,opt_str,value,parser):
    '''Convert hex string to int.

    optpars callback function.
    '''
    try:
        i = int(value,16)
    except ValueError,inst:
        parser.error('Please type a valid hexadecimal value')
    setattr(parser.values,option.dest,i)


def main():
    """Main program.

    Executing the file will start this function.
    """
    # OptionParser helps reading options from command line
    parser = OptionParser(
            usage='%prog [options]',
            version="%%prog, Hermod release %s" % (config.get('DEFAULT',
                                                              'version')),
            description="Find level1b files."
            )
    parser.set_defaults(datestart=datetime(2001,1,1),
            dateend = datetime.today(),
            orbitstart = 0x0000,
            orbitend = 0xFFFF,
            verbose = False,
            logfile = "",
            list = False,
            cal=[-1,-2],
            )
    parser.add_option('-s','--start-time',
            action='callback',callback=parsetime,dest='datestart',nargs=2,
            type='string',
            metavar='YYYYMMDD HH:MM',
            help='filter on start date default is 2 days from now'
            )
    parser.add_option('-k','--end-time',
            action='callback',callback=parsetime,dest='dateend',nargs=2,
            type='string',
            metavar='YYYYMMDD HH:MM',help='filter on stop date default is now'
            )
    parser.add_option('-o','--start-orbit',
            action='store',dest='orbitstart',type='int',
            metavar='ORB_START',help='add filter on start decimal orbit'
            )
    parser.add_option('-e','--end-orbit',
            action='store',dest='orbitend',type='int',
            metavar='ORB_END',help='filter on end decimal orbit'
            )
    parser.add_option('-O','--start-hexorbit',
            action='callback',callback=hex2dec,dest='orbitstart',type='string',
            metavar='HEX_ORB_START',help='filter on start hex orbit'
            )
    parser.add_option('-E','--end-hexorbit',
            action='callback',callback=hex2dec,dest='orbitend',type='string',
            metavar='HEX_ORB_END',help='filter on stop hex orbit'
            )
    parser.add_option('-l','--logfile',type='string',dest='logfile',
            metavar="LOG",help='Print all output to a logfile'
            )
    parser.add_option('-v','--verbose',action='store_true',dest='verbose',
            help='display info when launching to queue'
            )
    parser.add_option('-L','--list',action='store_true',dest='list',
            help='list - don''t run anythint just list files to download'
            )
    parser.add_option('-c','--calibration',
            action='append',dest='cal',type='float',
            metavar='CAL',help='calibration version'
            )
    (options, args) = parser.parse_args()

    # manipulate some values
    if len(options.cal)==2:
        n = range(20)
        setattr(parser.values,'cal',map(float,range(20)))

    l1 = findids(('''
        SELECT id FROM level1 l1 
        left join status s using (id) 
        left join level1b_gem l1b using (id) 
        where calversion in %s and s.status 
            and (l1b.date<l1.uploaded or l1b.filename is null) 
            and l1.filename is not null 
            and l1.orbit>=%s and l1.orbit<=%s
            and l1.stop_utc>=%s and l1.start_utc<=%s''',
        (options.cal,options.orbitstart,options.orbitend,options.datestart,
         options.dateend)
        ))
    close = False
    if options.verbose:
        l1.logfile= stderr
    if options.logfile!="":
        close=True
        l1.logfile=open(options.logfile,'wb')
    l1.setnames()
    if options.list:
        for id in l1.ids:
            print id.hdf
    else:
        l1.download()
    if close:
        l1.logfile.close()


if __name__=="__main__":
    main()
