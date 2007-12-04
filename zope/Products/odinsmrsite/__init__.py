# CMF imports
from Products.CMFCore.utils import ToolInit
from Products.CMFCore.DirectoryView import registerDirectory

# Configuration
from config import PRODUCT_NAME,GLOBALS,ICON,SKINS_DIR

# Import the tools
import downloaddata
import browsepictures
import managequeue

registerDirectory(SKINS_DIR,GLOBALS)

def initialize(context):
    # Assign the Project name and the objects attached to each tool
    init = ToolInit(
            PRODUCT_NAME,
            tools=(downloaddata.SearchAndDownload,
                browsepictures.BrowsePictures,
                managequeue.ManageQueue,
                ),
            icon=ICON,
            )
    init.initialize(context)

