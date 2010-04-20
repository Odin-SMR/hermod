import unittest
from tests import notest

def test_suite():
    return unittest.TestSuite([
        notest.test_suite(),
        ])

if __name__=="__main__":
    unittest.TextTestRunner(verbosity=3).run(test_suite())

