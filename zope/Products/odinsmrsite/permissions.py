#CMF imports
from Products.CMFCore.permissions import setDefaultRoles

BROWSE = 'odinsmrsite: Browse Pictures'
DOWNLOAD = 'odinsmrsite: Download Files'
MANAGE = 'odinsmrsite: Manage System'

setDefaultRoles(BROWSE,('Owner','Manager'))
setDefaultRoles(DOWNLOAD,('Owner','Manager'))
setDefaultRoles(MANAGE,('Owner','Manager'))
