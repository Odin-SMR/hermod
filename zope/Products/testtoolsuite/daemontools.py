from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
from Products.CMFCore.utils import UniqueObject,SimpleItemWithProperties
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from sys import stderr,exit
from os import fork, kill
from time import ctime, sleep
from StringIO import StringIO
class DaemonTool(UniqueObject,SimpleItemWithProperties,Folder):
    """A class in testtoolsuite.
    
    addable in ZMI testtool Class
    callable from ./daemontool
    """
    meta_type = 'Daemontool Class'
    id= 'daemontool'
    
    childpid = 0
    at_mask = '(at)'
    security = ClassSecurityInfo()
    security.declareObjectProtected('View')

    security.declareProtected('View','test')
    def rundaemon(self):
        """ A demo daemon main routine, write a datestamp to 
            /tmp/daemon-log every 10 seconds.
        """
	s = StringIO()
	print >> s, "Creating a report"
	if not hasattr(self,'forkreport'):
	    print >> stderr, "no folder named forkreport"
	    self.manage_addFolder('forkreport')
	print >>stderr, "sleep 5 secs"
	sleep(10)
	folder = getattr(self,'forkreport')
	print folder
	folder.manage_addDocument('report',title='Fork Report',file=s)
	print >>stderr, self
	exit(0)

    security.declareProtected('View','test')
    def stopdaemon(self):
        """If the self.childpid is not 0 kill that process.
        """
	if self.childpid:
    	    print self.childpid
	    kill(self.childpid,15) 


    security.declareProtected('View','test')
    def startdaemon(self):
	"""run code in the background.
	"""
        try: 
            pid = fork() 
            if pid ==0:
		print >>stderr,"child %s" % self
		self.rundaemon()
                exit(0) 
	    else:
		self.childpid=pid
        except OSError, e: 
            print >>stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror) 
	print >> stderr,"Parent %s" % self
   	return "Child %i started" % self.childpid 

InitializeClass(DaemonTool)

if __name__=="__main__":
    # if the script runs from commandline
    print "run"

	     
    
