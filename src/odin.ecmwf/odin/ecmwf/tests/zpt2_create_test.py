import mocker
from unittest import makeSuite,TestSuite,TextTestRunner,TestCase
from datetime import datetime
from odin.ecmwf.donalettyEcmwfNC import ZptFile
import odin.config.environment
from pkg_resources import resource_filename
from StringIO import StringIO
class ZPT2TestCase(mocker.MockerTestCase):
    def test_zpt2(self):
        #2011-07-15
        ztp=ZptFile('OC1BDD69.LOG','test.ztp2')
        #2011-05-15
        #ztp=ZptFile('OC1BD9D2.LOG','test.ztp2')



def test_suite():
    tests = [
            'test_zpt2',
            ]
    return TestSuite(map(ZPT2TestCase,tests))

if __name__=='__main__':
    TextTestRunner(verbosity=3).run(test_suite())


