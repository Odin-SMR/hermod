import unittest
from odin.ecmwf.tests import nc_create

def test_suite():
    return unittest.TestSuite([
        nc_create.test_suite(),
        ])

if __name__=="__main__":
    unittest.TextTestRunner(verbosity=3).run(test_suite())

