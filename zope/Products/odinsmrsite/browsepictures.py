from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import UniqueObject,SimpleItemWithProperties
from Products.CMFCalendar.CalendarTool import CalendarTool
from permissions import BROWSE
import DateTime

class BrowsePictures(SimpleItemWithProperties):
    """Browse and display quicklook images.

    Provides a browsable interface to the portal user to all quicklook images
    produced
    
    """
    meta_type = 'Browse and display Quicklook'

    #set up security
    security = ClassSecurityInfo()
    security.declareObjectProtected(BROWSE)

    security.declarePublic(BROWSE,'test')
    def test(self):
        return 

InitializeClass(BrowsePictures)
