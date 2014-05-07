import unittest
from odin.config.environment import config,HermodError,HermodWarning
import logging
import logging.config
from logging import StreamHandler
from logging.handlers import SocketHandler
from StringIO import StringIO
from pkg_resources import resource_stream

def getexcept(e):
    raise e

class EnvironmentTestCase(unittest.TestCase):
    def setUp(self):
        self.config = config()

    def config(self):
        sections = self.config.sections()
        testsection = ['GEM']
        for section in testsection:
            self.assertTrue(section in sections)

    def hermodWarning(self):
        self.assertRaises(HermodWarning,getexcept,HermodWarning)

    def hermodError(self):
        self.assertRaises(HermodError,getexcept,HermodError)

    def logger(self):
        log = StringIO()
        name=self.config.get('logging','configfile')
        file = resource_stream("odin.config",name)
        logging.config.fileConfig(file)
        logger = logging.getLogger('')
        logger.handlers.pop(0)#(SocketHandler('localhost',9020))
        logger.addHandler(StreamHandler(log))
        #logger.warning("test root")
        logger2=logging.getLogger('hermod')
        logger2.critical("test hermod")
        log.seek(0)
        #self.assertEqual(log.readline(),"test root\n")
        self.assertEqual(log.readline(),"test hermod\n")

def test_suite():
    tests = [
            'config',
            'logger',
            'hermodWarning',
            'hermodError',
            ]
    return unittest.TestSuite(map(EnvironmentTestCase,tests))

if __name__=='__main__':
    unittest.TextTestRunner(verbosity=3).run(test_suite())

