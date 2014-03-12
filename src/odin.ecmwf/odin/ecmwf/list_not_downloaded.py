from glob import glob
from odin.config.database import connect
from odin.config.environment import config,set_hermod_logging
from datetime import date
from time import strptime, mktime
from os import remove,symlink
from os.path import join,basename,exists,dirname
from odin.ecmwf.ecmwf_nc import makedir
from optparse import OptionParser
from sys import argv
import logging

def parsedate(option, opt_str, value, parser):
    '''Parse time string in YYYYMMDD format to date.

    optparse callback function.
    '''
    try:
        t = date.fromtimestamp(mktime(strptime('%s' % value, '%Y%m%d')))
    except ValueError:
        parser.error('Please type date according to ISO 8601 YYYYMMDD')
    setattr(parser.values, option.dest, t)

def run_query(datestart,dateend,type,limit):
    set_hermod_logging()
    log = logging.getLogger('list_not_downloaded')
    db = connect()
    cur = db.cursor()
    log.info('Searching not downloade AN- files with a {0}-limit'.format(limit))
    status = cur.execute('''
            SELECT rc.date, rt.time 
            from reference_calendar rc 
            join reference_time rt 
            left join (select date,hour from ecmwf where type=%s) 
                e on (rc.date=e.date and rt.time=e.hour)
            where  rc.date>%s and rc.date<%s 
                and e.hour is null
            order by rc.date desc,time
            limit %s''',(type,datestart,dateend,limit))
    log.info('Found {0}'.format(status))
    for day, hour in cur:
        print "{0} {1:02}".format(day,hour)

def main():
    """Main program.

    Executing the file will start this function.
    """
    # OptionParser helps reading options from command line
    parser = OptionParser(
            usage='%prog [options]',
            description="Finds AN-files that are available at ECMWF but not here"
            )
    parser.set_defaults(
                        datestart=date(2001,6,1),
                        dateend = date.today(),
                        type = "AN",
                        limit = 100,
                        )
    parser.add_option('-s', '--start-date',
            action='callback', callback=parsedate, dest='datestart', nargs=1,
            type='string', metavar='YYYYMMDD',
            help='filter on start date default is 20010601'
            )
    parser.add_option('-k', '--end-date',
            action='callback', callback=parsedate, dest='dateend', nargs=1,
            type='string', metavar='YYYYMMDD',
            help='filter on stop date default is today')
    parser.add_option('-t', '--type',
            action='store', nargs=1, dest='type',
            type='string', metavar='FILE_TYPE',
            help='one of AN,PV,T,Z - files to look for'
            )
    parser.add_option('-l', '--limit',
            action='store', nargs=1, dest='limit',
            type='int', metavar='LIMIT',
            help='limit the result to LIMIT number of files'
            )
    (options, args) = parser.parse_args(args=argv[1:]) #@UnusedVariable

    run_query(options.datestart,options.dateend,options.type,options.limit)

if __name__=="__main__":
    main()

