import unittest
import mocker
import odin.iasco.tracer_fields
import datetime

def getexcept(e):
    raise e

class TracerFieldsTestCase(mocker.MockerTestCase):
    def setUp(self):
        pass

    def hdfRead_test(self):
	"""Testing hdfRead 
	
	Checks that all the parts in the program runs as many times as they should for a specified orbit list, one date and fqid=3
	"""
        logconf = self.mocker.replace("logging.config.fileConfig")
        logconf(mocker.ANY)

        logmock = self.mocker.mock()
        logmock.info(mocker.ARGS,mocker.KWARGS)
    	
        logger = self.mocker.replace("logging.getLogger")
        logger(mocker.ANY)
        self.mocker.result(logmock) 
        self.mocker.count(2)
                
        session = self.mocker.mock()
        session.putstring(mocker.ARGS,mocker.KWARGS)
        
        session.run(mocker.ARGS,mocker.KWARGS)
        
        session.close(mocker.ARGS,mocker.KWARGS)
        
        matSess = self.mocker.replace("pymatlab.matlab.MatlabSession")
        matSess(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(session)

        self.mocker.replay()
        orbit_list = {'orbit': [0,],'start_utc': [datetime.date(2010,1,1),],'stop_utc': [datetime.date(2010,1,1),]}
        self.assertEquals(odin.iasco.tracer_fields.hdfRead(datetime.date(2010,1,1),orbit_list,3),None)
        self.mocker.verify()


def test_suite():
    tests = [
            'hdfRead_test',
            ]
    return unittest.TestSuite(map(TracerFieldsTestCase,tests))

if __name__=='__main__':
    unittest.TextTestRunner(verbosity=3).run(test_suite())
