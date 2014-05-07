from unittest import makeSuite,TestSuite,TextTestRunner
from datetime import date
from odin.hermod.ecmwf import MatlabMakeZPT,weatherfile
from odin.hermod.session import GEMMatlab
from os.path import exists,abspath,join
from os import remove
from sys import stderr
import mocker
from pkg_resources import resource_filename

class EcmwfTestCase(mocker.MockerTestCase):

    def ecmwf_make_zpt(self):
        "Testing making zpt"
#        config = self.mocker.mock()
#        config.get('GEM','LEVEL1B_DIR')
#        self.mocker.result("")
#
#        cfg = self.mocker.replace("odin.config.environment.config")
#        cfg()
#        self.mocker.result(config)
#
#        self.mocker.replay()
        class test(MatlabMakeZPT):
            pass
        mat = test()
        mat.m_session = GEMMatlab()
        mat.m_session.start_matlab()
        mat.zpt = resource_filename("odin.hermod","tests/OB1BC1D9.ZPT")
        mat.log = resource_filename("odin.hermod","tests/OB1BC1D9.LOG")
        self.assertEqual(mat.makeZPT(),mat.zpt)
        self.assertTrue(exists(mat.zpt))
        remove(mat.zpt)
        #self.mocker.verify()

    def ecmwf_get_gen_T(self):
        "Generate and download a PVfile from nilu"
        db = self.mocker.mock()
        testfile = weatherfile(db,'T',0,date(2008,12,17))
        testfile.localname = resource_filename("odin.hermod","tests/testfile")
        testfile.generate()
        testfile.download()
        self.assertTrue(exists(testfile.localname))
        remove(testfile.localname)




def test_suite():
    tests = [
            'ecmwf_make_zpt',
            'ecmwf_get_gen_T',
            ]
    return TestSuite(map(EcmwfTestCase,tests))

if __name__=='__main__':
    TextTestRunner(verbosity=3).run(test_suite())


