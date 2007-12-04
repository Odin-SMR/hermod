from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
from Products.CMFCore.utils import UniqueObject,SimpleItemWithProperties
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from threading import Thread
from transaction import commit,abort

from sys import stderr,exit
from os import fork, kill
from time import ctime, sleep
from StringIO import StringIO

class DaemonTool2(UniqueObject,SimpleItemWithProperties,Folder):
    """A class in testtoolsuite.
    
    addable in ZMI testtool Class
    callable from ./daemontool2

    This class provides the possibility to run jobs in the background using
    threads

    """
    meta_type = 'Daemontool2 Class'
    id= 'daemontool2'
    
    manage_options = Folder.manage_options
    security = ClassSecurityInfo()
    security.declareObjectProtected('View')

    security.declareProtected('View','startPage')
    startPage = PageTemplateFile('www/start.pt',globals())

    security.declareProtected('View','startdaemon')
    def startdaemon(self):
	"""run code in the background.
	"""
        _a = Daemon()
        _a.setDaemon(True)
        _a.start()
        return "Started, yes"

class Daemon(Thread):
    """A Thread.
    """
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        try:
            from transaction import begin,commit,Transaction
            from Zope2 import DB
            conn = DB.open()
            root = conn.root()
            app = root['Application']
            sleep(15)
            if not hasattr(app,'testiparent'):
                app.manage_addDocument('testiparent')
                print >>stderr,"ok,done: adding..."
                commit()
            else:
                print >>stderr,"ok,done: not adding ..."
                abort()
            conn.close()
        except Exception,text:
            print >>stderr,"rundaemon: %s"%text

InitializeClass(DaemonTool2)

if __name__=="__main__":
    # if the script runs from commandline
    print "run"

	     
    
