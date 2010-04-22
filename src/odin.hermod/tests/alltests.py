import unittest
from tests import test_session,test_pdc

def test_suite():
    return unittest.TestSuite([
        test_session.test_suite(),
        test_pdc.test_suite(),
        ])

if __name__=="__main__":
    unittest.TextTestRunner(verbosity=3).run(test_suite())

