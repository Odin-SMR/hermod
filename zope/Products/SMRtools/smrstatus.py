import MySQLdb
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from OFS.Folder import Folder
from AccessControl import ClassSecurityInfo

from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.utils import UniqueObject,SimpleItemWithProperties

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

import matplotlib
matplotlib.use('Agg')
from pylab import *
from sys import stdout,stderr
from os import *
from StringIO import StringIO
from PIL import Image as PILImage
from OFS.Image import Image,manage_addImage
from matplotlib.backends.backend_agg import FigureCanvasAgg
from subprocess import Popen,PIPE
from hermod.hermodBase import *
import numpy
from datetime import datetime,timedelta

from config import *
#class SMRstatus(UniqueObject,Folder,ActionProviderBase):
class SMRstatus(UniqueObject,SimpleItemWithProperties):
    """prints some stats"""
    meta_type = PROJECTNAME
    id= 'smrstatus'
    at_mask = '(at)'
    connectionStr = {'host':'jet','user':'gem','db':'smr'}
    
    security = ClassSecurityInfo()
    security.declareObjectProtected('View')

    security.declareProtected('View', 'outputPage')
    outputPage = PageTemplateFile('www/output.pt',GLOBALS)
    
    security.declareProtected('View_data','dataPage')
    dataPage =   PageTemplateFile('www/data.pt',GLOBALS)
    
    security.declareProtected('View Status','statusPage')
    statusPage =   PageTemplateFile('www/status.pt',GLOBALS)

    security.declareProtected('View Status','lastPage')
    lastPage =   PageTemplateFile('www/last.pt',GLOBALS)

    security.declareProtected('View Status','managePage')
    managePage =   PageTemplateFile('www/manage.pt',GLOBALS)
    
#    manage_options = ( {'label':'output','action':'outputPage'})+ ActionProviderBase.manage_options 
#    manage_options = ( {'label':'output','action':'outputPage'},)+ ActionProviderBase.manage_options+Folder.manage_options
#    manage_options = Folder.manage_options + ActionProviderBase.manage_options 
#    _properties = Folder._properties + ( {'id':'at_mask','type':'string','mode':'w',},)
    security.declareProtected('View', 'getNumber')

    def getNumber(self):
    	"""docstrinc"""
#    	x=[1234]
        db = MySQLdb.connect(**self.connectionStr)
	cursor = db.cursor()
        s = cursor.execute('''SELECT count(distinct filename) from level1 natural join status where calversion=6 and status''')
        x = cursor.fetchone()
        db.close()
	return x[0]

    security.declareProtected('View Status', 'currentList')
    def currentList(self):
        """docstring"""
        p = Popen(['/usr/bin/qstat','-r','-n','-1'],stdin=PIPE,stdout=PIPE,stderr=PIPE,close_fds=True)
        out,err, = p.communicate()
        if err=='':
            outlines = out.splitlines()[5:]
            outlinessplitted = [i.split() for i in outlines]
            return outlinessplitted
        else:
            return None
    
    security.declareProtected('View Status','lastList')
    def lastList(self):
        """docstring"""
        db = MySQLdb.connect(**self.connectionStr)
        cursor = db.cursor()
        #set boundings for the query
        datestart = datetime.now() - timedelta(days=1)
        dateend = datetime.now()
        orbitstart = 0
        orbitend =0xFFFF
        fqid = range(1,50)
        try:
            status=cursor.execute("""
                    select l2.processed,start_utc,orbit,freqmode,fqid,version,
                        l1.nscans,l2.nscans,l2.nscans/l1.nscans as proc,verstr,hdfname,id 
                    from level1 as l1 
                    join level2files as l2 using (id) 
                    where l2.processed>=%s and l2.processed<=%s and orbit>=%s 
                        and orbit<=%s and fqid in %s and l1.nscans<>0 
                    order by l2.processed;
                    """,
                    (datestart,dateend,orbitstart,orbitend,fqid)
                )
        except Warning,inst:
            print >> stderr, "Warning: %s" % inst
        except StandardError,inst:
            print >> stderr, "Error: %s" % inst
            cursor.close()
            db.close()
            return None
        lines = cursor.fetchall()
        cursor.close()
        db.close()
        return lines


    security.declareProtected('View', 'displayStats')
    def displayStats(self):
    	'''docstnci'''
        user = self.portal_membership.getAuthenticatedMember()
        clf()
        img_dpi=72
        width=400
        height=300
        fig=figure(dpi=img_dpi, figsize=(width/img_dpi, height/img_dpi))
        x=arange(0, 2*pi+0.1, 0.1)
        sine=plot(numpy.random.randn(100))
        legend(sine, "y=sin x", "upper right")
        xlabel('x')
        ylabel('y=sin x')
        grid(True)
        canvas = FigureCanvasAgg(fig)
        canvas.draw()
        size = (int(canvas.figure.get_figwidth())*img_dpi, int(canvas.figure.get_figheight())*img_dpi)
        buf=canvas.tostring_rgb()
        im=PILImage.fromstring('RGB', size, buf, 'raw', 'RGB', 0, 1)
        im_pic = StringIO()
        im.save(im_pic,'PNG')
        id = "%s_test_pic" % user
        tempid = getattr(self,'odin')
        if tempid is None:
            tempid = self
            print "no temp"
            print tempid
        if hasattr(tempid,id):
            tempid.manage_delObjects([id])
        tempid.manage_addImage(id,im_pic,title='test picture',content_type='image/png')
        return id

    security.declareProtected('View', 'displayStatsR')
    def displayStatsR(self):
    	'''docstnci'''
        clf()
        img_dpi=72
        width=400
        height=300
        fig=figure(dpi=img_dpi, figsize=(width/img_dpi, height/img_dpi))
        x=arange(0, 2*pi+0.1, 0.1)
        sine=plot(x, sin(x))
        legend(sine, "y=sin x", "upper right")
        xlabel('x')
        ylabel('y=sin x')
        grid(True)
        canvas = FigureCanvasAgg(fig)
        canvas.draw()
        size = (int(canvas.figure.get_figwidth())*img_dpi, int(canvas.figure.get_figheight())*img_dpi)
        buf=canvas.tostring_rgb()
        im=PILImage.fromstring('RGB', size, buf, 'raw', 'RGB', 0, 1)
        im_pic = StringIO()
        im.save(im_pic,'PNG')
        self.REQUEST.RESPONSE.setHeader('Pragma','no-cache')
        self.REQUEST.RESPONSE.setHeader('Content-Type','image/png')
        return im_pic.getvalue()
        
    security.declareProtected('View', 'displayReq')
    def displayReq(self,test):
        '''docstring'''
	print test
	print self.REQUEST.items()

    security.declareProtected('View', 'displayPic')
    def displayPic(self,test):
        '''docstring'''
	file = '/odin/smr/Data/SMRl2/SMRquicklook/Qsmr-2-1/SM_AC2ab/l2zonalmean.%s.l1b-v6_l2-v2.1.TEMP_ECMWF.Tpot.jpg'
	im = PILImage.open(file % (test,))
	im.load()
	im_pic = StringIO()
	im.save(im_pic,'JPEG')
	if hasattr(self.testfolder,test):
	    self.testfolder.manage_delObjects([test])
	self.testfolder.manage_addImage(test, im_pic, title='zonalmean-%s' % (test,) , content_type='image/jpeg')
	print "info:",im.info
	print "format:",im.format
	print "mode:",im.mode

def test():
    x = SMRstatus()
    stdout.write('create figure\n')
    x.displayStats()
    stdout.write('counting files\n')
    n = x.getNumber()
    stdout.write('found %i files\n'%(n,))

def main():
    x = SMRstatus()
    print x.getNumber()

InitializeClass(SMRstatus)

if __name__=="__main__":
    main()
	     
    
