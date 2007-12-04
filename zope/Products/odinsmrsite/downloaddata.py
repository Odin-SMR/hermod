from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import UniqueObject

from permissions import DOWNLOAD

class SearchAndDownload(UniqueObject):
    """Search and download l1 and l2 data.

    Tool to provide the search and download data from the web

    """
    meta_type = 'Search and download data'
    id = 'data_download'

    #set up security
    security = ClassSecurityInfo()
    security.declareObjectProtected(DOWNLOAD)

InitializeClass(SearchAndDownload)
