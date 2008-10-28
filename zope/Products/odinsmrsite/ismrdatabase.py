class ISMRDataBase:
    """Interface to make database lookups.

    This Interface defines how to make lookups in the database from plone.

    """
    
    def searchData(self,**SearchParameters):
        """Make a search with arbitrary kewords.
        
        input:Keywords comes from a request

        Output: a list of dictinaries with results from the smr database. 

        Establish a connection to the database for each lookup.
        """
        raise NotImplementedError, "Subclasses must implement searchData"


    def downloadData(self,**downLoadList):
        """Make a gzip-tarball and return to RESPONSE-object.

        Input: list of filenames to download

        Result is written to self.REQUEST.Response object.
        creates a gzip-tarball and send it to the client.
        """
        raise NotImplementedError, "Subclasses must implement downloadData"
