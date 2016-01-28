#!/usr/bin/env python
from migrate.versioning.shell import main

if __name__ == '__main__':
    main(url='mysql://odinuser:***REMOVED***@mysqlhost/hermod', debug='False', repository='hermod')
