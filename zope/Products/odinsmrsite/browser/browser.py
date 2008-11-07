from Products.Five import BrowserView
from Products.odinsmrsite.interfaces.interfaces import IPicturePolicy

class PictureView(BrowserView):
    def picturesAllowed(self,site=False):
        policy = IPicturePolicy(self.context)
        allowed = True
        if not site and not policy.picturesAllowed:
            allowed= False
        if site and not policy.sitePicturesAllowed:
            allowed= False

        if not allowed:
            raise ValueError, "not allowed"
        return allowed


