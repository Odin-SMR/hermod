import unittest
import mocker
import odin.iasco.winds
import datetime

def getexcept(e):
    raise e

class WindsTestCase(mocker.MockerTestCase):
    def setUp(self):
        pass

    def extractWinds_test(self):
	"""Testing extractWinds 
	
	Test that the program parts runs as many times as expected for one date.
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
        self.assertEquals(odin.iasco.winds.extractWinds(datetime.date(2010,1,1)),None)
        self.mocker.verify()


    def copyWinds_test(self):
	"""Testing copyWinds
	
	   It is only a test where the file exists. Quite a nonsense test.
	"""
        logconf = self.mocker.replace("logging.config.fileConfig")
        logconf(mocker.ANY)
    	
        logger = self.mocker.replace("logging.getLogger")
        logger(mocker.ANY) 
        self.mocker.count(2)
        
        path = self.mocker.replace("os.path.exists")
        path(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(True)
        self.mocker.count(100)

        self.mocker.replay()
        self.assertEquals(odin.iasco.winds.copyWinds(datetime.date(2010,1,1)),None)
        self.mocker.verify()

def test_suite():
    tests = [
            'extractWinds_test',
            'copyWinds_test',
            ]
    return unittest.TestSuite(map(WindsTestCase,tests))

if __name__=='__main__':
    unittest.TextTestRunner(verbosity=3).run(test_suite())
