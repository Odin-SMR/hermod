import unittest
from odin.hermod.tests import test_session,test_pdc,test_ecmwf,test_interfaces,test_pbs

def test_suite():
    return unittest.TestSuite([
        test_session.test_suite(),
        test_pdc.test_suite(),
        test_pbs.test_suite(),
        test_ecmwf.test_suite(),
        test_interfaces.test_suite(),
        ])

if __name__=="__main__":
    unittest.TextTestRunner(verbosity=3).run(test_suite())

