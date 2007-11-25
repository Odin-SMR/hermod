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

    ## Defining a Pagtemplate found in www
    security.declareProtected('View', 'helloPage')
    helloPage = PageTemplateFile('www/hello.pt',globals())

    security.declareProtected('View','test')
    def test(self):
        """Simple hello world.

        callable function from /testtool/test
        """
        return 'hello world'
    
InitializeClass(TestTool)

if __name__=="__main__":
    print "run"

	     
    
