import unittest
import mocker
import odin.iasco.pics
import logging
import logging.config
import datetime


def getexcept(e):
    raise e

class picsTestCase(mocker.MockerTestCase):
    def setUp(self):
        pass

    def makePictures_test(self):
        """Testing makePictures
        
        """
        gPlot = self.mocker.replace("odin.iasco.plot.globalPlot")
        self.mocker.result(None)

        pPlot = self.mocker.replace("odin.iasco.plot.polarPlot")
        self.mocker.result(None)
     	
     	#zopestd = self.mocker.mock()
     	#zopestd.write(mocker.ARGS,mocker.KWARGS)
     	
        #zope = self.mocker.mock()
        #zope.stdin(mocker.ARGS,mocker.KWARGS)
        #self.mocker.result(zopestd)
        
        #z = self.mocker.replace("zope.stdin.write")
        #z(mocker.ARGS,mocker.KWARGS)
        #self.mocker.result(None)
        
        path = self.mocker.replace("os.path.exists")
        path(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(True)
        
        self.assertEquals(odin.iasco.pics.makePictures(datetime.date(2010,1,1),29,''))

def test_suite():
    tests = [
            #'makePictures_test',
            ]
    return unittest.TestSuite(map(picsTestCase,tests))

if __name__=='__main__':
    unittest.TextTestRunner(verbosity=3).run(test_suite())

