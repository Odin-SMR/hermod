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
        from MySQLdb.cursors import DictCursor
        db = connect(**connection_str)
        query = """
            select distinct l2f.id,l2f.fqid,version,hdfname,orbit 
            from level1 as l1
                join level2files as l2f
                    on (l1.id=l2f.id)
                join level2 as l2 
                    on (l2f.id=l2.id and l2f.fqid=l2.fqid and l2f.version=l2.version2) 
            where 1 %s
            order by date
            """
        
        where = ""
        
        webparams = dict(**params)
        # add where clause for time filter
        if webparams['form.select_time']=='utc':
            where = where+ " and date>=%(form.start_utc)s and date<=%(form.stop_utc)s\n"
        elif webparams['form.select_time']=='mjd':
            where = where+ " and mjd>=%(form.start_mjd)s and mjd<=%(form.stop_mjd)s\n"
        elif webparams['form.select_time']=='orb':
            where = where+ " and orbit>=%(form.start_orb)s and orbit<=%(form.stop_orb)s\n"
        elif webparams['form.select_time']=='hex':
            where = where+ " and hex(orbit)>=%(form.start_hex)s and hex(orbit)<=%(form.stop_hex)s\n"
        # add where clause for location filter
        if webparams['form.select_location']=='rad':
            where = where + " and 6375*acos( sin(latitude*pi()/180) * sin(%(form.lat)s*pi()/180) \n+ cos(latitude*pi()/180) * cos(%(form.lat)s*pi()/180) * cos(-longitude*pi()/180+%(form.lon)s*pi()/180)) < %(form.radius)s\n"
        # add mode constraints
        if webparams['form.select_species']=='fqid':
            tuple = self.removePrefix(webparams,'form.fqid',int) 
            where = where + " and l2.fqid in %s" %str(tuple)
        elif webparams['form.select_species']=='fm':
            tuple = self.removePrefix(webparams,'form.fm',int)
            where = where + " and freqmode in %s" %str(tuple)
        elif webparams['form.select_species']=='short':
            tuple = self.removePrefix(webparams,'form.name_',str)
            #where = where + " and name in %s" %str(tuple)

        #add version constraint
        if webparams['form.select_processors']=='vers':
            tuple = self.removePrefix(webparams,'form.processors_',str) 
            where = where + " and version2 in %s" %str(tuple)


        cursor = db.cursor(DictCursor)
        finalQuery = query %(where,)
        print finalQuery
        cursor.execute(finalQuery,webparams)
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        return rows

    security.declarePrivate('removePrefix')
    def removePrefix(self,dictionary,prefix,type_constructor):
        ''' return a tuple of values with a common prefix'''
        list = map(type_constructor,[0,255]) # Dummy values
        for i in dictionary.keys():
            if i.startswith(prefix):
                value = i.replace(prefix,'')
                list.append(type_constructor(value))
        return tuple(list)
        

    security.declareProtected(DOWNLOAD,'downloadData')
    def downloadData(self,**params):
        '''Get the actual data as a gz-tarball.

        Returns the data matched with searchData as a gzipped tarball.
        '''
        from StringIO import StringIO
        from subprocess import Popen,PIPE
        from hermod.hermodBase import config
        webparams = dict(**params)
        response = self.REQUEST.RESPONSE
        response.setHeader('Pragma','no-cache')
        response.setHeader('content-coding','gzip')

        #create a list of selected filenames
        filenames = [i[0] for i in webparams.items() if i[1]=='on']

        # create a series of pipes "tar | gzip > response"
        tarball = Popen(['tar','-c']+filenames,stdout=PIPE,cwd=config.get('GEM','SMRl2_DIR'))
        gzip = Popen(['gzip','--fast'],stdin=tarball.stdout,stdout=PIPE)
        while True:
            data = gzip.stdout.read(256)
            if data =="":
                break
            else:
                response.write(data)
        tarball.stdout.close()
        gzip.stdout.close()

    security.declareProtected(DOWNLOAD,'getAvailProcessors')
    def getAvailProcessors(self):
        from hermod.hermodBase import connection_str
        from MySQLdb import connect
        db = connect(**connection_str)
   
        cursor = db.cursor()
        cursor.execute('SELECT distinct qsmr FROM odin.Versions order by qsmr')
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        return [("form.processors_"+x[0],x[0]) for x in rows]

    security.declareProtected(DOWNLOAD,'getAvailFqids')
    def getAvailFqids(self):
        from hermod.hermodBase import connection_str
        from MySQLdb import connect
        db = connect(**connection_str)
   
        cursor = db.cursor()
        cursor.execute('SELECT distinct fqid FROM odin.Versions where active order by fqid')
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        return [("form.fqid"+str(x[0]),"fqid "+str(x[0])) for x in rows]

    security.declareProtected(DOWNLOAD,'getAvailFms')
    def getAvailFms(self):
        from hermod.hermodBase import connection_str
        from MySQLdb import connect
        db = connect(**connection_str)
   
        cursor = db.cursor()
        cursor.execute('SELECT distinct freqmode FROM odin.Versions where active order by freqmode')
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        return [("form.fm"+str(x[0]),"freqmode "+str(x[0])) for x in rows]

    security.declareProtected(DOWNLOAD,'getAvailNames')
    def getAvailNames(self):
        from hermod.hermodBase import connection_str
        from MySQLdb import connect
        db = connect(**connection_str)
   
        cursor = db.cursor()
        cursor.execute('SELECT name FROM odin.Versions V natural join odin.Freqmodes where active order by name')
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        return [("form.name_"+str(x[0]),str(x[0])) for x in rows]


InitializeClass(SearchAndDownload)
