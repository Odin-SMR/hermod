"""
Odin transparent database connection.
"""

from MySQLdb.connections import Connection
from MySQLdb.cursors import Cursor
from odin.config.environment import config
from pkg_resources  import resource_filename
import logging

class OdinCursor(Cursor):
    """Odin Cursor class.
    """
    def __init__(self, *args, **kwargs):
        Cursor.__init__(self, *args, **kwargs)
        self.log = logging.getLogger(__name__)
        self.log.debug('Created a cursor')
    
    def execute(self, *args, **kwargs):
        status =Cursor.execute(self, *args, **kwargs)
        self.log.debug('Fired a query: ' +str(args) + str(kwargs))
        return status
            
    def close(self):
        Cursor.close(self)
        self.log.debug('Closed cursor')

class ConnectionServer(Connection):
    """A Connection class with logger capabilities.
    """
    def __init__(self, *args, **kwargs):
        if not kwargs.has_key('cursorclass'):
            kwargs['cursorclass'] = OdinCursor
        Connection.__init__(self, *args, **kwargs)
        self.log = logging.getLogger(__name__)
        self.log.debug(" ".join([
                "Connected to",
                self.get_host_info(),
                "with thread id: ",
                str(self.thread_id()),
                ]))
        
    def close(self):
        self.log.debug(" ".join([
                "Closing connection to",
                self.get_host_info(),
                "thread id: ",
                str(self.thread_id()),
                ]))
        Connection.close(self)

def connect():
    """Factory to return a MySQL.Connections.Connection.
    """
    conf = config()
    return ConnectionServer(host=conf.get('WRITE_SQL', 'host'),
                db=conf.get('WRITE_SQL', 'db'),
                user=conf.get('WRITE_SQL', 'user'),
                passwd=conf.get('WRITE_SQL', 'passwd'))
