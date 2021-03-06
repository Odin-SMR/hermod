#!/usr/bin/python
"""Display information from processing system.

Command line tool to see what files have been processed during a given timespan.
"""

from odin.hermod.hermodBase import config,connetion_str
from sys import exit,stderr
from optparse import OptionParser
from os import environ
from datetime import datetime,timedelta
from time import strptime,mktime
from MySQLdb import connect
from MySQLdb.cursors import DictCursor

def parsetime(option,opt_str,value,parser):
    """Parse a string YYYYMMDD HH:MM to time.

    Function is designed to fit optparse - to run as a callback function.
    """
    try:
        t = datetime.fromtimestamp(mktime(strptime('%s %s' % value,'%Y%m%d %H:%M')))
    except ValueError:
        parser.error('Please type date according to ISO 8601 YYYYMMDD HH:MM')
    setattr(parser.values,option.dest,t)

def hex2dec(option,opt_str,value,parser):
    """Convert string Hex to int.

    Function has the parameter format to fit optparse's calback action.
    """
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
            usage='%prog [options] [DAYS]',
            version="%%prog, Hermod %s" % (config.get('DEFAULT','version')),
            description="Display information about processed file during a given timespan. Default behaivior is to display the latest 2 days. The DAYS parameter overides the -s option."
            )
    parser.set_defaults(datestart=datetime.today()-timedelta(2),
            dateend = datetime.today(),
            orbitstart = 0x0000,
            orbitend = 0xFFFF,
            verbose = False,
            fqid =[127] #dummy value
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
    parser.add_option('-f','--fqid',action='append',dest='fqid',type='int',
            metavar='FQID',help='filter on fqids'
            )
    parser.add_option('-v','--verbose',action='store_true',dest='verbose',
            help='show more info, but wider rows'
            )
    (options, args) = parser.parse_args()

    if len(options.fqid)==1:
        #only the dummy value add all fqids
        setattr(parser.values,'fqid',range(1,40))

    if len(args)>=1:
        # lastdays
        try:
            i = int(args[0])
            setattr(parser.values,'datestart',datetime.today()-timedelta(i))
        except ValueError,inst:
            pass

    # Initiate a database connection
    try:
        db = connect(**connection_str)
    except Warning,inst:
        print >> stderr, "Warning: %s" % inst
    except Error,inst:
        print >> stderr, "Error: %s" % inst
        exit(1)

    c = db.cursor(DictCursor)

    # Retrieve info from database
    try:
        status=c.execute("""
        select l2.processed,start_utc,orbit,freqmode,fqid,version,
            l1.nscans,l2.nscans,l2.nscans/l1.nscans as proc,verstr,hdfname,id 
        from level1 as l1 
        join level2files as l2 using (id) 
        where l2.processed>=%s and l2.processed<=%s and orbit>=%s 
            and orbit<=%s and fqid in %s and l1.nscans<>0 
        order by l2.processed;""",
        (options.datestart,options.dateend,options.orbitstart,options.orbitend,
         options.fqid))
    except Warning,inst:
        print >> stderr, "Warning: %s" % inst
    except StandardError,inst:
        print >> stderr, "Error: %s" % inst
        exit(1)

    # Print
    if options.verbose:
        print "%-19s%10s%7s%21s%8s%4s%6s%4s%4s%5s%12s%55s" % ('processed',
                                                              'dbid','orb','start_utc','fm','fq','ver','ps','ts','%','verstr','file')
    else:
        print "%-19s%10s%7s%8s%4s%6s%4s%4s%5s%12s" % ('processed','dbid','orb','fm','fq','ver','ps','ts','%','verstr')

    for row in c:
        if options.verbose:
            print "%(processed)s%(id)10i%(orbit)7.4X%(start_utc)21s%(freqmode)8s%(fqid)4.2i%(version)6s%(l2.nscans)4i%(nscans)4i%(proc)5.1f%(verstr)12s%(hdfname)55s" % row
        else:
            print "%(processed)s%(id)10i%(orbit)7.4X%(freqmode)8s%(fqid)4.2i%(version)6s%(l2.nscans)4i%(nscans)4i%(proc)5.1f%(verstr)12s" % row
            
    c.close()
    db.close()

#Starts the program if it is started from a shell.
if __name__=="__main__":
    main()


