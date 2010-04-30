import unittest
import mocker
import odin.iasco.assimilation
import datetime

def getexcept(e):
    raise e

class AssimilationTestCase(mocker.MockerTestCase):
    def setUp(self):
        pass

    def assimilate(self):
	"""Testing assimilation 

	"""
        logconf = self.mocker.replace("logging.config.fileConfig")
        logconf(mocker.ANY)

        logmock = self.mocker.mock()
        logmock.info(mocker.ARGS,mocker.KWARGS)
    	self.mocker.count(3)
    	
        logger = self.mocker.replace("logging.getLogger")
        logger(mocker.ANY)
        self.mocker.result(logmock) 
        self.mocker.count(2)
        
        session = self.mocker.mock()
        session.putstring(mocker.ARGS,mocker.KWARGS)
        self.mocker.count(3)
        
        session.run(mocker.ARGS,mocker.KWARGS)
        self.mocker.count(3)
        
        session.close(mocker.ARGS,mocker.KWARGS)
        
        matSess = self.mocker.replace("pymatlab.matlab.MatlabSession")
        matSess(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(session)

        self.mocker.replay()
        self.assertEquals(odin.iasco.assimilation.assimilate(datetime.date(2010,1,1),3),None)
        self.mocker.verify()


def test_suite():
    tests = [
            'assimilate',
            ]
    return unittest.TestSuite(map(AssimilationTestCase,tests))

if __name__=='__main__':
    unittest.TextTestRunner(verbosity=3).run(test_suite())
