from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase

DESIGNER = 'Erik Zakrisson, Marcus Jansson'

class CreditsViewlet(ViewletBase):
    render = ViewPageTemplateFile('colophon.pt')

    def update(self):
        # set here the values that you need to grab from the template.
        # stupid example:
        self.designer = DESIGNER

