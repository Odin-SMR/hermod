from unittest import TestCase,makeSuite,TestSuite
from odin.config.environment import config_files,config,connection_str


class NoTestCase(TestCase):

    def test1(self):
        self.assertEqual(1,1);

    def testT(self):
        self.assertTrue(True);

class TestConfig(TestCase):
    def testConfig(self):
        self.assert_(config_files!=[])
	pass


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NoTestCase))
    suite.addTest(makeSuite(TestConfig))
    return suite


