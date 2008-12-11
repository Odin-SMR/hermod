#!/usr/bin/python

"""Get weather data from Nilu.

Generate and download weather data from Nilu. Processing is done at 
zardoz.nilu.no. 
"""

from optparse import OptionParser
from os import environ
from sys import exit, stderr

from MySQLdb import connection

from hermod.ecmwf import weathercontrol
from hermod.hermodBase import connection_str, config

def main():
    """Main program.

    Executing this file will run this function.
    """
    # OptionParser helps reading options from command line
    parser = OptionParser(
            version="%%prog, Hermod %s" % (config.get('DEFAULT', 'version')), 
            description="Generate and download weather data files from nilu"
            )
    (options, args) = parser.parse_args()
    try:
        user = environ['USER']
    except KeyError, inst:
        parser.error("No, user environment found")
    if user<>'odinop':
        parser.error("User %s in not allowed to run this program" % user)

    #Initiate the database
    try:
        db = connect(**connection_str)
    except Warning, inst:
        print >> stderr, "Warning: %s" % inst
    except Error, inst:
        print >> stderr, "Error: %s" % inst
        exit(1)

    # generate,download,find T,Z,U,V and PV
    t=weathercontrol(db, 'T')
    t.find()
    t.generate()
    z=weathercontrol(db, 'Z')
    z.find()
    z.generate()
    pv=weathercontrol(db, 'PV')
    pv.find()
    pv.generate()
    u=weathercontrol(db, 'U')
    u.find()
    u.generate()
    v=weathercontrol(db, 'V')
    v.find()
    v.generate()
    db.close()

if __name__=="__main__":
    main()
