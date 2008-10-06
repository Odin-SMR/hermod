from Products.CMFCore import permissions
from Products.Archetypes.atapi import *
from Products.odinsmrsite.config import PRODUCT_NAME
schema = BaseSchema.copy() +  Schema((


  TextField('body',
            searchable = 1,
            required = 1,
            allowable_content_types = ('text/plain',
                                       'text/structured',
                                       'text/html',),
            default_output_type = 'text/x-html-safe',
            widget = RichWidget(label = 'Message body'),
           ),

))

class control(BaseContent):
    """ An Archetype for an InstantMessage application """

    schema = schema
    meta_type = portal_type = 'Controller'
    archetype_name = 'Controller'

    _at_rename_after_creation = True
    actions = ({
        'id'          : 'view',
        'name'        : 'View',
        'action'      : 'string:${object_url}',
        'permissions' : (permissions.View,)
         },
        {
        'id'          : 'edit',
        'name'        : 'Edit',
        'action'      : 'string:${object_url}/edit',
        'permissions' : (permissions.ModifyPortalContent,),
         },
        {
        'id'          : 'metadata',
        'name'        : 'Properties',
        'action'      : 'string:${object_url}/properties',
        'permissions' : (permissions.ModifyPortalContent,),
         },
        )
    aliases = {
        '(Default)'  : 'controller_view',
        'view'       : 'controller_view',
        'edit'       : 'base_edit',
        'properties' : 'base_metadata',
        }

registerType(control, PRODUCT_NAME)
