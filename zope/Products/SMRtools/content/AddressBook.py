from Products.Archetypes.atapi import *
from Products.SMRtools.config import PROJECTNAME

AddressBookSchema = BaseSchema

ContactSchema = BaseSchema + Schema((
    StringField('name'),
    StringField('email'),
    StringField('homepage'),
    ))

class AddressBook(BaseFolder):
    """specialized folder for managing contact information"""

    archetype_name = "Address Book"

    filter_content_types = 1
    allowed_content_types = ('Contact',)

    schema = AddressBookSchema

registerType(AddressBook,PROJECTNAME)

class Contact(BaseContent):
    """entry in an address book"""

    global_allow = 0

    schema = ContactSchema

registerType(Contact,PROJECTNAME)
