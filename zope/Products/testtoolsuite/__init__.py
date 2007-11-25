
from Products.CMFCore import utils

# Import the tools
import testtools

def initialize(context):
    
    utils.ToolInit('TestTools Suite', tools=(testtools.TestTool,),icon='tool.gif',).initialize(context)
