from Products.CMFCore import permissions
from Products.odinsmrsite.config import PRODUCT_NAME

from Products.Archetypes.BaseContent import BaseContent, BaseSchema
from Products.Archetypes.Schema import Schema
from Products.Archetypes.ArchetypeTool import registerType
from Products.Archetypes.Widget import ImageWidget,StringWidget,LabelWidget
from Products.Archetypes.Field import ImageField,StringField,ComputedField


from cStringIO import StringIO

from PIL import Image as PILImage
# import from the graphics package

class Controller (BaseContent):
  """ plot  """
  # Add an ImageField to your schema
  # Read up on the deails of ImageField, it has nice features like scaling
  schema = BaseSchema + Schema((
    ImageField('myImage',
               default_content_type='image/png',
               widget=ImageWidget(label="Generated Image",display_threshold=1000000,modes=('view'))
	       ,max_size=(640,480)
              ),
    StringField('date',
              widget=StringWidget(label='Date',modes=('edit')),
              ),
  ))
  meta_type = portal_type = 'Diagram'
  archetype_name = 'display a diagram'
  _at_rename_after_creation = True

  aliases = {
        '(Default)'  : 'base_view',
        'view'       : 'base_view',
        'edit'       : 'base_edit',
        'properties' : 'base_metadata',
        }

  def at_post_create_script(self):
      '''docstring'''
      date = self.getDate()
      self.genPic(date)

  def at_post_create_script(self):
      '''docstring'''
      date = self.getDate()
      self.genPic(date)

  def genPic(self,date='2007-08-19'):
        '''docstring'''
	file = '/odin/smr/Data/SMRl2/SMRquicklook/Qsmr-2-1/SM_AC2ab/l2zonalmean.%s.l1b-v6_l2-v2.1.TEMP_ECMWF.Tpot.jpg'
	im = PILImage.open(file % (date,))
	im.load()
	im_pic = StringIO()
	im.save(im_pic,'JPEG')
	self.setMyImage(im_pic,mimetype='image/jpeg')

registerType(Controller,PRODUCT_NAME)
