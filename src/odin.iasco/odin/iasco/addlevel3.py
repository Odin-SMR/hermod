import Zope2
from Zope2 import configure

from AccessControl.SecurityManagement import newSecurityManager
from Products.CMFCore.utils import getToolByName

import transaction
from DateTime import DateTime
from Products.ATContentTypes.content.folder import ATFolder

def main():
    conf =configure('/usr/local/Plone/zinstance/parts/instance/etc/zope.conf')
    app = Zope2.app()
    smr = app['OdinSMR']
    user = app.acl_users.getUser('admin').__of__(app.acl_users)
    newSecurityManager(None, user)
    while 1:
        try:
            a =raw_input()
        except EOFError:
	    break
        year,month,day,species,level, = a.split(',')
        createLevel3Object(smr,year,month,day,species,level)



def createLevel3Object(site,year,month,day,species,level):
    potLevel={'N2O':['475K','525K','575K','625K'],'O3_501':['475K','525K','575K','625K'],'O3_544':['475K','525K','575K','625K'],'HNO3':['475K','525K','575K','625K','675K','725K'],'H2O':['400K','425K','450K','475K','500K','525K']}
    specTitle={'N2O':['nitrous oxide', '501.8 Ghz'],'O3_501':['ozone', '501.8 Ghz'],'O3_544':['ozone', '544.6 Ghz'],'HNO3':['nitric acid', '544.6 Ghz'],'H2O':['water vapour', '544.6 Ghz']}
    date='%s-%02d-%02d'%(year,int(month),int(day))
    item="%s_%s_%s"%(date,species,level)
    t=transaction.get()
    rootFolder = 'Level4'
    if not hasattr(site,rootFolder):
        site[rootFolder]=ATFolder(rootFolder)
        wftool = getToolByName(site[rootFolder],'portal_workflow')
        try:
            wftool.doActionFor(site[rootFolder],'publish')
        except Exception:
            pass
        site[rootFolder].reindexObject()
        
    if not site[rootFolder].hasObject(species):
        site[rootFolder][species]=ATFolder(species)
        wftool = getToolByName(site[rootFolder][species],'portal_workflow')
        try:
            wftool.doActionFor(site[rootFolder][species],'publish')
        except Exception:
            pass
        site[rootFolder][species].reindexObject()
    
    if not site[rootFolder][species].hasObject(year):
        site[rootFolder][species][year]=ATFolder(year)
        wftool = getToolByName(site[rootFolder][species][year],'portal_workflow')
        try:
            wftool.doActionFor(site[rootFolder][species][year],'publish')
        except Exception:
            pass
        site[rootFolder][species][year].reindexObject()
    
    if not site[rootFolder][species][year].hasObject(month):
        site[rootFolder][species][year][month]=ATFolder(month)
        wftool = getToolByName(site[rootFolder][species][year][month],'portal_workflow')
        try:
            wftool.doActionFor(site[rootFolder][species][year][month],'publish')
        except Exception:
            pass
        site[rootFolder][species][year][month].reindexObject()
            
    if site[rootFolder][species][year][month].hasObject(item):
        site[rootFolder][species][year][month].manage_delObjects(item)
        
    site[rootFolder][species][year][month].invokeFactory('Level3Product',item)
    
    a = site[rootFolder][species][year][month][item]
    a.title=u'Image of assimilated data for %s studied at %s and potential temperature level %s, %s'%(specTitle[species][0],specTitle[species][1],potLevel[species][int(level)],date)
    a.description =u"Level 3 product"
    start_date='%s 00:00'%date
    end_date='%s 23:59'%date
    a.start = DateTime(start_date)
    a.end = DateTime(end_date)
    a.species = unicode(species)
    a.level = unicode(level)
    a.year = unicode(year)
    a.month = unicode(month)
    a.day = unicode(day)
    
    wftool = getToolByName(a,'portal_workflow')
    try:
        wftool.doActionFor(a,'publish')
    except Exception:
        pass
         
    a.reindexObject()
    t.commit()

if __name__=='__main__':
    main()


