import unittest
import mocker
import odin.iasco.convert_date
import logging
import logging.config
import datetime


def getexcept(e):
    raise e

class Convert_dateTestCase(mocker.MockerTestCase):
    def setUp(self):
        pass

    def mjd2utc_test(self):
        """Testing mjd2utc
        
        Checking if mjd2utc returns the expected utc date 
        """
        self.assertEquals(odin.iasco.convert_date.mjd2utc(52183),(2001, 10, 1, 0, 0, 0, 0))

    def utc2mjd_test(self):
        """Testing utc2mjd
        
        Checking if utc2mjd returns the expected mjd date
        """
        self.assertEquals(odin.iasco.convert_date.utc2mjd(2001,10,01),52183)


def test_suite():
    tests = [
            'mjd2utc_test',
	    'utc2mjd_test',
            ]
    return unittest.TestSuite(map(Convert_dateTestCase,tests))

if __name__=='__main__':
    unittest.TextTestRunner(verbosity=3).run(test_suite())

