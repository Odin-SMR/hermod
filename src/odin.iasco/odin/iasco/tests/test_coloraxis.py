import unittest
import mocker
import odin.iasco.color_axis
import logging
import logging.config
import datetime


def getexcept(e):
    raise e

class Color_axisTestCase(mocker.MockerTestCase):
    def setUp(self):
        pass

    def caxis(self):
        """Testing color_axis
	
	Checking if color_axis.py returns the expected caxis and step for a specific level and species
        """
        self.assertEquals(odin.iasco.color_axis.c_axis(0,'O3_501'),((0,4), 0.5))

def test_suite():
    tests = [
            'caxis',
            ]
    return unittest.TestSuite(map(Color_axisTestCase,tests))

if __name__=='__main__':
    unittest.TextTestRunner(verbosity=3).run(test_suite())

