import unittest
from odin.config.environment import config,HermodError,HermodWarning
import logging
import logging.config
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

    def HermodError(self):
        self.assertRaises(HermodError,getexcept,HermodError)

    def logger(self):
        name=self.config.get('logging','configfile')
        file = resource_stream("odin.config",name)
        logging.config.fileConfig(file)

        


def test_suite():
    tests = [
            'config',
            'logger',
            ]
    return unittest.TestSuite(map(EnvironmentTestCase,tests))

if __name__=='__main__':
    unittest.TextTestRunner(verbosity=3).run(test_suite())

