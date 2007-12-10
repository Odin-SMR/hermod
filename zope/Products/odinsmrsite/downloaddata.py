from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import UniqueObject,SimpleItemWithProperties

from permissions import DOWNLOAD

class DataBaseInterface:
    """Abstract class defines how to make database lookups.

    place for unittests?
    """
    def searchL2(self,**SearchParameters):
        """Make a search with arbitrary kewords.

        Input: a dictionary with searchparameters
        Output: a list of dictinaries with results. 

        >>> a = DataBaseInterface()
        >>> a.searchL2({'start_orbit':0x8000,'stop_orbit':0x8FFF,'fqid':29'}
        ... [{'orbit':0x801F,'species':'ClO, O_3, N_2O','version':'2-1'},{'orbit':0x8020,'species':'ClO, O_3, N_2O','version':'2-1'}]

        """
        return  [{'orbit':0x801F,'species':'ClO, O_3, N_2O','version':'2-1'},{'orbit':0x8020,'species':'ClO, O_3, N_2O','version':'2-1'}]

    def downloadL2(self,downLoadList):
        """Make a gzip-tarball and return to RESPONSE-object.

        Input: Same kind of list of dictionaries created by searchL2(...) .

        Result is written to self.REQUEST.Response object.

        >>> a = DataBaseInterface()
        >>> a.downLoadL2(a.search({'start_orbit':0x8000,'stop_orbit':0x8FFF,'fqid':29'}))

        creates a gzip-tarball and send it to the client.

        """
        pass

    def status(self,typ):
        """ print status"""
        print type(typ)
        print typ

class SearchAndDownload(DataBaseInterface,UniqueObject,SimpleItemWithProperties):
    """Search and download l1 and l2 data.

    Tool to provide the search and download data from the web

    """
    meta_type = 'Search and download data'
    id = 'data_download'

    #set up security
    security = ClassSecurityInfo()
    security.declareObjectProtected(DOWNLOAD)

    #set up security for inherited functions
    security.declareProtected(DOWNLOAD,'searchL2')
    security.declareProtected(DOWNLOAD,'downloadL2')
    security.declareProtected(DOWNLOAD,'form')
    def form(self):
        """Validates a form.
        """
        print self.REQUEST.get('name',None)
        pt = self.getParentNode()
        print pt.id
        return pt.search(name='test')

InitializeClass(SearchAndDownload)
