"""
Juno transparent database connection.
"""

from MySQLdb.connections import Connection
from MySQLdb.cursors import Cursor
from juno.common.environment import config, logger
from os import walk
from os.path import join
import logging
try:
    import sqlite3
except:
    pass




logger()

class JunoCursor(Cursor):
    """Juno Cursor class.
    """
    def __init__(self, *args, **kwargs):
        Cursor.__init__(self, *args, **kwargs)
        self.log = logging.getLogger('JunoCursor')       
        self.log.debug('Created a cursor')
        pass
    
    def execute(self, *args, **kwargs):
        status =Cursor.execute(self, *args, **kwargs)
        self.log.info('Fired a query: ')
        return status
            
    def close(self):
        Cursor.close(self)
        self.log.debug('Closed cursor')

class FakeJunoCursor(JunoCursor):
    """Fake Juno Cursor class.
    """
    def __init__(self, *args, **kwargs):
        self.log = logging.getLogger('FakeJunoCursor')
        self.log.info('Created a cursor')
        self.conf = config()
        pass
    
    def __iter__(self):
        return self
    
    def next(self):
        if len(self.queue) == 0:
            raise StopIteration
        return (self.queue.pop(),)
        
    
    def execute(self, *args, **kwargs):
        self.log.debug('fired a query')
        queue = []
        for root, dirs, files in walk(self.conf.get('Amaterasu', 'datastorage')):
            for f in files:
                if f.endswith('.l1b'):
                    queue.append(join(root, f))
        self.queue = queue[:self.conf.getint('MySQL', 'fake_max_results')]
        self.log.debug('Fired a query :%i rows')
        return len(self.queue)
    
    def fetchone(self):
        if len(self.queue) == 0:
            return None
        return (self.queue.pop(),)        
    
    def close(self):
        self.log.debug('Closed Fake cursor')
        

class ConnectionServer(Connection):
    """A Connection class with logger capabilities.
    """
    def __init__(self, *args, **kwargs):
        if not kwargs.has_key('cursorclass'):
            kwargs['cursorclass'] = JunoCursor
        Connection.__init__(self, *args, **kwargs)
        self.log = logging.getLogger('ConnectionServer')
        self.log.info(self.get_host_info())
        
    def close(self):
        self.log.info('Database connection closing')
        Connection.close(self)

class ConnectionFake(Connection):
    def __init__(self, *args, **kwargs):
        self.arg = args
        self.kwargs = kwargs
        self.log = logging.getLogger('ConnectionFake')
        self.log.info(self.get_host_info())

    def get_host_info(self):
        return "FakeServer at localhost"
    
    def cursor(self, *args, **kwargs):
        return FakeJunoCursor()
    
    def close(self):
        self.log.info('Database is closed')

def connect():
    """Factory to return a MySQL.Connections.Connection.
    """
    conf = config()
    type = conf.get('MySQL', 'type')
    if type == 'server':
        return ConnectionServer(host=conf.get('MySQL', 'host'),
                db=conf.get('MySQL', 'db'),
                user=conf.get('MySQL', 'user'),
                passwd=conf.get('MySQL', 'password'))
    elif type == 'file':
        return sqlite3.connect(conf.get('MySQL','file'))
    else:
        return ConnectionFake()
