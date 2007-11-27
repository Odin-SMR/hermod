
from Products.CMFCore import utils

# Import the tools
import testtools
import daemontools
def initialize(context):
    
    utils.ToolInit('TestTools Suite', tools=(testtools.TestTool,daemontools.DaemonTool,),icon='tool.gif',).initialize(context)
