#!/usr/bin/python
"""Find level1 files.
"""

from MySQLdb import connect
from MySQLdb.cursors import DictCursor
from datetime import datetime, timedelta
from odin.hermod.hermodBase import connection_str, config
from optparse import OptionParser
from os import environ
from os.path import join, splitext, exists
from sys import exit, stderr
from time import strptime, mktime


def parsetime(option, opt_str, value, parser):
    '''Parse time string in YYYYMMDD HH:MM format to time.

    optparse callback function.
    '''
    try:
        t = datetime.fromtimestamp(mktime(strptime('%s %s' % value, 
                                                   '%Y%m%d %H:%M')))
    except ValueError:
        parser.error('Please type date according to ISO 8601 YYYYMMDD HH:MM')
    setattr(parser.values, option.dest, t)

def hex2dec(option, opt_str, value, parser):
    '''Convert hex string to int.

    optpars callback function.
    '''
    try:
        i = int(value, 16)
    except ValueError, inst:
        parser.error('Please type a valid hexadecimal value')
    setattr(parser.values, option.dest, i)


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
    parser.set_defaults(datestart=datetime(2001, 1, 1), 
            dateend = datetime.today(), 
            orbitstart = 0x0000, 
            orbitend = 0xFFFF, 
            verbose = False, 
            launch = False, 
            cal=[-1, -2], 
            fm =[127, 128], 
            threshold = .1, 
            queue = 'rerun', 
            qsmr= '2-1')
    parser.add_option('-s', '--start-time', 
            action='callback', callback=parsetime, dest='datestart', nargs=2, 
            type='string', metavar='YYYYMMDD HH:MM', 
            help='filter on start date default is 2 days from now'
            )
    parser.add_option('-k', '--end-time', 
            action='callback', callback=parsetime, dest='dateend', nargs=2, 
            type='string', metavar='YYYYMMDD HH:MM', 
            help='filter on stop date default is now'
            )
    parser.add_option('-o', '--start-orbit', 
            action='store', dest='orbitstart', type='int', 
            metavar='ORB_START', help='add filter on start decimal orbit'
            )
    parser.add_option('-e', '--end-orbit', 
            action='store', dest='orbitend', type='int', 
            metavar='ORB_END', help='filter on end decimal orbit'
            )
    parser.add_option('-O', '--start-hexorbit', 
            action='callback', callback=hex2dec, dest='orbitstart', 
            type='string', metavar='HEX_ORB_START', 
            help='filter on start hex orbit'
            )
    parser.add_option('-E', '--end-hexorbit', 
            action='callback', callback=hex2dec, dest='orbitend', type='string', 
            metavar='HEX_ORB_END', help='filter on stop hex orbit'
            )
    parser.add_option('-f', '--freqmode', action='append', dest='fm', 
                      type='int', metavar='FM', help='filter on freqmode'
            )
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose', 
            help='display info when launching to queue'
            )
    parser.add_option('-c', '--calibration', 
            action='append', dest='cal', type='float', 
            metavar='CAL', help='calibration version'
            )
    (options, args) = parser.parse_args()

    # manipulate some values
    if len(options.cal)==2:
        n = range(20)
        setattr(parser.values, 'cal', map(float, range(20)))

    if len(options.fm)==2:
        n = range(50)
        setattr(parser.values, 'fm', n)

    # Initiate a database connection
    try:
        db = connect(host=config.get('READ_SQL','host'),
            user=config.get('READ_SQL','user'),
            db=config.get('READ_SQL','db'))
    except Warning, inst:
        print >> stderr, "Warning: %s" % inst
    except Exception, inst:
        print >> stderr, "Error: %s" % inst
        exit(1)


    #find orbitfiles to run
    cursor = db.cursor(DictCursor)
    try:
        status = cursor.execute('''select filename,logname from level1 
                                   where 1 
                                   and orbit>=%s 
                                   and start_utc>=%s
                                   and orbit<=%s 
                                   and stop_utc<=%s
                                   and freqmode in %s and calversion in %s 
                                   order by orbit,backend,calversion
                                   ''', (options.orbitstart, options.datestart, 
                                         options.orbitend, options.dateend, 
                                         options.fm, options.cal))
    except Warning, e:
        print >> stderr, "Hermod:", str(e)
    except Exception, e:
        print >> stderr, "Hermod:", str(e)
        exit(3)
    except KeyboardInterupt:
        print >> stderr, "Hermod: KeyboardInterrupt, closing database..."
        cursor.close()
        db.close()
        exit(2)

    # do desired action on every object
    for i in cursor:
            try:
                if not (i['filename'] is None):
                    file = join(config.get('GEM', 'LEVEL1B_DIR'), 
                                splitext(i['filename'])[0])
                    if exists(file):
                        print file
            except HermodError, inst:
                print >> stderr, 'HermodError: %s'%inst 
                continue
    cursor.close()
    db.close()

if __name__=="__main__":
    main()
