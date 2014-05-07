import mocker
from unittest import makeSuite,TestSuite,TextTestRunner,TestCase
from datetime import datetime
from pkg_resources import resource_filename
import odin.config.environment
import odin.config.database
import odin.ecmwf.create_odinecmwf
class RunEcmwfTestCase(mocker.MockerTestCase):

    def maintest(self):
        e = self.mocker.mock()
        e.convert2nc()
        e.convert2odin()
        e.cpfile()
        e.delete()
        e.outfile()
        self.mocker.count(2,2)
        self.mocker.result(resource_filename(
                'odin.ecmwf','.')+'/1976/10/file.nc')
        e.time.date()
        self.mocker.result('76-10-09')
        e.time.hour
        self.mocker.result('00')
 
        ecmwf = self.mocker.replace(odin.ecmwf.ecmwf_nc.Ecmwf_Grib2)
        ecmwf(mocker.ANY)
        self.mocker.result(e)

        conf = self.mocker.mock()
        conf.get('ecmwf','spooldir')
        self.mocker.result(resource_filename('odin.ecmwf','tests'))
        conf.get('ecmwf','basedir')
        self.mocker.result(resource_filename('odin.ecmwf','.'))

        config = self.mocker.replace(odin.config.environment.config)
        config()
        self.mocker.result(conf)
 
        log = self.mocker.replace(odin.config.environment.set_hermod_logging)
        log()
        
        curs = self.mocker.mock()
        curs.execute(mocker.ANY,mocker.ANY)
        curs.close()

        database = self.mocker.mock()
        database.cursor()
        self.mocker.result(curs)
        database.close()
        
        con = self.mocker.replace(odin.config.database.connect)
        con()
        self.mocker.result(database)

        self.mocker.replay()

        odin.ecmwf.create_odinecmwf.create_insert()

def test_suite():
    tests = [
            'maintest',
            ]
    return TestSuite(map(RunEcmwfTestCase,tests))

if __name__=='__main__':
    TextTestRunner(verbosity=3).run(test_suite())


