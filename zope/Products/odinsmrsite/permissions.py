#CMF imports
from Products.CMFCore.permissions import setDefaultRoles
from Products.Archetypes.atapi import listTypes
from config import PRODUCT_NAME

BROWSE = '%s: Browse Pictures' % PRODUCT_NAME
DOWNLOAD = '%s: Download Files' % PRODUCT_NAME
MANAGE = '%s: Manage System' % PRODUCT_NAME

ADD_PICTURES = '%s: Add Data Pictures' % PRODUCT_NAME

setDefaultRoles(BROWSE,('Owner','Manager'))
setDefaultRoles(MANAGE,('Owner','Manager'))
setDefaultRoles(DOWNLOAD,('Owner','Manager'))
setDefaultRoles(ADD_PICTURES,('Owner','Manager'))
