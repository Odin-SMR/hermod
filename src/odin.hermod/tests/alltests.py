import unittest
from tests import test_session

def test_suite():
    return unittest.TestSuite([
        test_session.test_suite()
        ])

if __name__=="__main__":
    unittest.TextTestRunner(verbosity=3).run(test_suite())

