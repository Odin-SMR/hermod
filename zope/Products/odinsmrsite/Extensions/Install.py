# CMF imports
from Products.CMFCore.utils import getToolByName

# Archetypes imports
from Products.Archetypes.ArchetypeTool import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin, install_tools

# Products imports
from Products.odinsmrsite.config import GLOBALS, PRODUCT_NAME

# Python imports
from StringIO import StringIO
    
def install(self):
    """Install content types, skin layer, enable the portal factory
    """

    out = StringIO()

    print >> out, "Installing %s" %PRODUCT_NAME

    # Install skin
    install_subskin(self, out, GLOBALS)
    print >> out, " Installed skin"

    # Install tools
    install_tools(self, out)
    print >> out, " Install tools"

    #add 'Data' to portal_tabs
    atool = getToolByName(self,'portal_actions')
    if atool.getActionObject('portal_tabs/data_tab') is None:
        atool.addAction('data_tab','data','string:$portal_url/search','python:member is not None','View','portal_tabs')
    if atool.getActionObject('portal_tabs/pict_tab') is None:
        atool.addAction('pict_tab','pictures','string:$portal_url/chooser','python:member is not None','View','portal_tabs')
    if atool.getActionObject('portal_tabs/admin_tab') is None:
        atool.addAction('admin_tab','admin','string:$portal_url/display','python:member is not None','View','portal_tabs')
    print >>out, "  Added %s in portal_tabs" %('all tabs')
    return out.getvalue()

