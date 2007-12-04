from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import UniqueObject,SimpleItemWithProperties

from permissions import MANAGE

class ManageQueue(UniqueObject,SimpleItemWithProperties):
    """Manages the processing queue.

    Provides a interface to the user to run, rerun, delete processes in the
    processing queue
    
    """

    meta_type = 'Manage processing queue'
    id = 'manage_queue'

    #set up security
    security = ClassSecurityInfo()
    security.declareObjectProtected(MANAGE)

InitializeClass(ManageQueue)
