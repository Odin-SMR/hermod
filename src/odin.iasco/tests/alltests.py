import unittest
from tests import test_blackbox

def test_suite():
    return unittest.TestSuite([
        test_blackbox.test_suite()
        ])

if __name__=="__main__":
    unittest.TextTestRunner(verbosity=3).run(test_suite())

