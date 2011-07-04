import mocker
from unittest import makeSuite,TestSuite,TextTestRunner,TestCase
from datetime import datetime
from odin.ecmwf.ecmwf_nc import Ecmwf_Grib2
import odin.config.environment
class EcmwfTestCase(mocker.MockerTestCase):

    def test_convert_grib(self):
	grib = Ecmwf_Grib2('ECMWF_ODIN_201105211800+000H00M')
        grib.convert2nc()
   
    def test_convert_nc(self):
	grib = Ecmwf_Grib2('ECMWF_ODIN_201105211800+000H00M')
        grib.convert2odin()

    def test_infile(self):
        time = datetime(1976,10,9,8,22)
        grib = Ecmwf_Grib2('ECMWF_ODIN_197610090822+000H00M')
        self.assertEqual(grib.time,time)

    def test_outfile(self):
        dir = self.mocker.mock()
        dir.get(mocker.ANY,mocker.ANY)
        self.mocker.result('/basedir/')

        conf = self.mocker.replace(odin.config.environment.config)
        conf()
        self.mocker.result(dir)
        self.mocker.replay()

        time = datetime(1976,10,9,8,22)
        grib = Ecmwf_Grib2('ECMWF_ODIN_197610090822+000H00M')
        grib.nlev = 91
        self.assertEqual(grib.outfile(),
                '/basedir/1976/10/ODIN_NWP_1976_10_0908_22_00_00_91_AN.NC')


def test_suite():
    tests = [
            'test_convert_grib',
            'test_convert_nc',
            'test_infile',
            'test_outfile',
            ]
    return TestSuite(map(EcmwfTestCase,tests))

if __name__=='__main__':
    TextTestRunner(verbosity=3).run(test_suite())


