from zope.schema import Bool, Iterable, TextLine
from zope.interface import Interface

class IController(Interface):
    """just a marker?
    """

class IPortalObject(Interface):
    """Another marker
    """
class IPicturePolicy(Interface):

    picturesAllowed = Bool(
        title=u"Is pictures allowed",
        description=u"Flags whether pictures is allowed",
        required=True,
        readonly=True
        )

    sitePicturesAllowed = Bool(
        title=u"Is site pictures allowed",
        description=u"Flags whether site pictures is allowed",
        required=True,
        readonly=True
        )

    pictureContent = Iterable(
        title=u"Picture Content",
        description=u"An iterable containing picture content objects",
        required=True,
        readonly=True
        )

    updateBase = TextLine(
        title=u"Update base",
        description=u"Date of the last update, in HTML4 format",
        required=True,
        readonly=True
        )
