#!/usr/bin/env python
from migrate.versioning.shell import main
import os

if __name__ == '__main__':
    connectstring=os.getenv('ODIN_DB_CONNECT', 'mysql://user:paswd@host/db')
    main(url=connectstring, debug='False', repository='hermod')
