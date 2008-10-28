from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import UniqueObject,SimpleItemWithProperties

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

class TestTool(UniqueObject,SimpleItemWithProperties):
    """A class in testtoolsuite.
    
    addable in ZMI testtool Class
    callable from ./testtool
    """
    meta_type = 'testtool Class'
    id= 'testtool'
    
    security = ClassSecurityInfo()
    security.declareObjectProtected('View')

    ## Defining a Pagetemplate found in www
    security.declareProtected('View', 'helloPage')
    helloPage = PageTemplateFile('www/hello.pt',globals())

    security.declareProtected('View','test')
    def test(self):
        """Simple hello world.

        callable function from /testtool/test
        """
        return 'hello world'

    security.declareProtected('View','tester')
    def tester(self):
        """Simple streaming response

        callable function from /testtool/tester
        """
        from time import sleep
        response = self.REQUEST.RESPONSE
        response.setHeader('Pragma','no-cache') 
        response.setHeader('Content-Type','text/plain') 
        for i in range(5):
            sleep(1)
            response.write(str(i)+'\n')
            response.flush()



InitializeClass(TestTool)

if __name__=="__main__":
    print "run"

	     
    
