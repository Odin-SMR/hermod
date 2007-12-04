#CMF imports
from Products.CMFCore.permissions import setDefaultRoles

BROWSE = 'SMR_Browse_Pictures'
DOWNLOAD = 'SMR_Download_Data'
MANAGE = 'SMR_Manage_Queue'

setDefaultRoles(BROWSE,('Owner','Manager'))
setDefaultRoles(DOWNLOAD,('Owner','Manager'))
setDefaultRoles(MANAGE,('Owner','Manager'))
