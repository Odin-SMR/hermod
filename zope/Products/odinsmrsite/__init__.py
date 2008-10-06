# CMF imports
from Products.Archetypes.atapi import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory

from content import *
# Configuration
from config import PRODUCT_NAME,GLOBALS,SKINS_DIR
from permissions import BROWSE,DOWNLOAD,MANAGE,ADD_PICTURES

registerDirectory(SKINS_DIR,GLOBALS)

def initialize(context):
    content_types, constructors, ftis = process_types(listTypes(PRODUCT_NAME),PRODUCT_NAME)

    utils.ContentInit(
            "%s Content" % PRODUCT_NAME,
            content_types      = content_types,
            permission         = ADD_PICTURES,
            extra_constructors = constructors,
            fti                = ftis,
            ).initialize(context)
