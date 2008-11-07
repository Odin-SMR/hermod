from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from Products.odinsmrsite.interfaces.interfaces import IPicturePolicy

class CMFPolicy(object):
    implements(IPicturePolicy)
    #adapts(IPortalContent)

    def __init__(self, context):
        self.context = context
        self.ps = getToolByName(self.context, "portal_syndication")

    def pictureAllowed(self, site=False):
        return self.ps.isSyndicationAllowed(self.context)
    syndicationAllowed = property(syndicationAllowed)

    def sitePictureAllowed(self):
        return self.ps.isSiteSyndicationAllowed()
    siteSyndicationAllowed = property(siteSyndicationAllowed)

    def PictureContent(self):
        return self.ps.getSyndicatableContent(self.context)
    syndicatableContent = property(syndicatableContent)

    def updateBase(self):
        return self.ps.getHTML4UpdateBase(self.context)
    updateBase = property(updateBase)
