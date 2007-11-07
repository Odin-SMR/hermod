# Python imports
from StringIO import StringIO

# CMF imports
from Products.CMFCore.utils import getToolByName

# Archetypes imports
from Products.Archetypes.ArchetypeTool import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin, install_tools

# Products imports
from Products.SMRtools.config import GLOBALS, PROJECTNAME

    
def install(self):
     """Install content types, skin layer, enable the portal factory
     """

     out = StringIO()

     print >> out, "Installing %s" %PROJECTNAME

     # Install types
     classes = listTypes(PROJECTNAME)
     installTypes(self, out, classes,PROJECTNAME)
     print >> out, " Installed type:"
     for i in classes:
         print >> out, "    %s" %(i['name'],)
	 
     # Install skin
     install_subskin(self, out, GLOBALS)
     print >> out, " Installed skin"

     # Install tools
     install_tools(self, out)
     print >> out, " Install tools"

     # Register types with portal_factory
     factory = getToolByName(self, 'portal_factory')
     types = factory.getFactoryTypes().keys()
     print >> out, " Added to portalfactory:"
     for k in classes:
	 i = k['name']
         if i not in types:
             types.append(i)
	     print >> out, "    %s" %(i)
     factory.manage_setPortalFactoryTypes(listOfTypeIds = types)

     return out.getvalue()

def uninstall(self):
    out = StringIO()
    print >> out, "Uninstalling %s" %PROJECTNAME
    classes = listTypes(PROJECTNAME)
    print >> out," Uninstalled type:"
    for i in classes:
        print >> out , "    %s" %(i['name'])
    factory = getToolByName(self, 'portal_factory')
    types = factory.getFactoryTypes().keys()
    print >> out, " Removed from portalfactory:"
    for k in classes:
        i=k['name']
        if i in types:
            types.remove(i)
        print >> out, "    %s" %(i)
    factory.manage_setPortalFactoryTypes(listOfTypeIds = types)

    return out.getvalue()
     
