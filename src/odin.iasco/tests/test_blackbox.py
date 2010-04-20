import unittest
import mocker
from odin.iasco.blackbox_main import main

def getexcept(e):
    raise e

class BlackboxTestCase(unittest.TestCase):
    def setUp(self):
        self.main = main()

    def noDates(self):
	main = self.mocker.mock()
	main.getNewDates()
	self.mocker.result([])
	main.getStartDate()
	self.mocker.result([])
        


def test_suite():
    tests = [
            'noDates',
            ]            ]
    return unittest.TestSuite(map(BlackboxTestCase,tests))

if __name__=='__main__':
    unittest.TextTestRunner(verbosity=3).run(test_suite())

