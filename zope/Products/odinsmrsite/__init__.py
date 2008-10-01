# CMF imports
from Products.CMFCore.DirectoryView import registerDirectory
# Configuration
from config import PRODUCT_NAME,GLOBALS,ICON,SKINS_DIR

from permissions import BROWSE,DOWNLOAD,MANAGE

registerDirectory(SKINS_DIR,GLOBALS)

#setDefaultRoles(BROWSE,('Owner','Manager'))
#setDefaultRoles(DOWNLOAD,('Owner','Manager'))
#setDefaultRoles(MANAGE,('Owner','Manager'))
