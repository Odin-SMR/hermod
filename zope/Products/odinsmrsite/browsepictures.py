from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import UniqueObject,SimpleItemWithProperties

from permissions import BROWSE

class BrowsePictures(UniqueObject,SimpleItemWithProperties):
    """Browse and display quicklook images.

    Provides a browsable interface to the portal user to all quicklook images
    produced
    
    """
    meta_type = 'Browse and display Quicklook'
    id = 'browse_quick'

    #set up security
    security = ClassSecurityInfo()
    security.declareObjectProtected(BROWSE)

InitializeClass(BrowsePictures)
