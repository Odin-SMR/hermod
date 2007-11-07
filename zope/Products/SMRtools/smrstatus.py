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
from sys import stdout
from os import *
from StringIO import StringIO
from PIL import Image as PILImage
from OFS.Image import Image,manage_addImage
from matplotlib.backends.backend_agg import FigureCanvasAgg

from config import *
class SMRstatus(UniqueObject,Folder,ActionProviderBase):
    """prints some stats"""
    meta_type = PROJECTNAME
    id= 'smrstatus'
    at_mask = '(at)'
    connectionStr = {'host':'jet','user':'gem','db':'smr'}
    outputPage = PageTemplateFile('www/output.pt',GLOBALS)
    
    security = ClassSecurityInfo()
    security.declareProtected(VIEW_PERMISSION, 'outputPage')
    
    #manage_options = ( {'label':'output','action':'outputPage'})+ ActionProviderBase.manage_options 
    manage_options = Folder.manage_options + ActionProviderBase.manage_options 
    _properties = Folder._properties + ( {'id':'at_mask','type':'string','mode':'w',},)
    security = ClassSecurityInfo()
    security.declareProtected(VIEW_PERMISSION, 'getNumber')

    def getNumber(self):
    	"""docstrinc"""
#    	x=[1234]
        db = MySQLdb.connect(**self.connectionStr)
	cursor = db.cursor()
        s = cursor.execute('''SELECT count(distinct filename) from level1 natural join status where calversion=6 and status''')
        x = cursor.fetchone()
        db.close()
	return x[0]

    security = ClassSecurityInfo()
    security.declareProtected(VIEW_PERMISSION, 'displayStats')
    def displayStats(self):
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
        if hasattr(self,'joakim_test_pic'):
            self.manage_delObjects(['joakim_test_pic'])
        self.manage_addImage('joakim_test_pic',im_pic,title='test picture',content_type='image/png')
        
    security = ClassSecurityInfo()
    security.declareProtected(VIEW_PERMISSION, 'displayReq')
    def displayReq(self,test):
        '''docstring'''
	print test
	print self.REQUEST.items()

    security = ClassSecurityInfo()
    security.declareProtected(VIEW_PERMISSION, 'displayPic')
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

if __name__=="__main__":
    main()
	     
    
