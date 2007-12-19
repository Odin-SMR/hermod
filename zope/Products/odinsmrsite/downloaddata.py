from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import UniqueObject,SimpleItemWithProperties

from permissions import DOWNLOAD
from ismrdatabase import ISMRDataBase


class SearchAndDownload(ISMRDataBase,UniqueObject,SimpleItemWithProperties):
    """Search and download l1 and l2 data.

    Tool to provide the search and download data from the web

    """
    meta_type = 'Search and download data'
    id = 'data_download'

    #set up security
    security = ClassSecurityInfo()
    security.declareObjectProtected(DOWNLOAD)

    #set up security for inherited functions
    security.declareProtected(DOWNLOAD,'searchData')

    def searchData(self,**params):
        '''Implementation of ISMRDataBase

        Get all parameters from the web-request and transform it to a sql-query
        '''
        from hermod.hermodBase import connection_str
        from MySQLdb import connect
        db = connect(**connection_str)
        webparams = dict(**params)
        if webparams['form.select_location']=='none':
            #no location filter
            pass
        else:
            #location filter
            pass
        db.close()
        return [1,2,3]

    security.declareProtected(DOWNLOAD,'downloadData')
    def downloadData(listOfResultsFromSearchData):
        '''Get the actual data as a gz-tarball.

        Returns the data matched with searchData as a gzipped tarball.
        '''
        pass


InitializeClass(SearchAndDownload)
