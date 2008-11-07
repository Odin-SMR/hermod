from cStringIO import StringIO

# CHANGE the following import lines to make them use your product name
from Products.odinsmrsite.Extensions.utils import *
from Products.odinsmrsite.config import *

def install(self):
    out = StringIO()

    setupSkins(self, out, GLOBALS, SKINSELECTIONS, SELECTSKIN, DEFAULTSKIN,
                          ALLOWSELECTION, PERSISTENTCOOKIE)
    registerResources(self, out, 'portal_css', STYLESHEETS)
    registerResources(self, out, 'portal_javascripts', JAVASCRIPTS)
    if DISPLAY_VIEWS:
        setupDisplayViews(self, out, DISPLAY_VIEWS)

    print >> out, "Installation completed."
    return out.getvalue()


def uninstall(self):
    out = StringIO()

    removeSkins(self, out, SKINSELECTIONS, DEFAULTSKIN, RESETSKINTOOL)
    resetResources(self, out, 'portal_css', STYLESHEETS)
    resetResources(self, out, 'portal_javascripts', JAVASCRIPTS)
    if DISPLAY_VIEWS:
        removeDisplayViews(self, out, DISPLAY_VIEWS)
