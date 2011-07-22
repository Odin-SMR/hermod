import unittest
from odin.ecmwf.tests import nc_create,create_insert_test
def test_suite():
    return unittest.TestSuite([
        create_insert_test.test_suite(),
        nc_create.test_suite(),
        ])

if __name__=="__main__":
    unittest.TextTestRunner(verbosity=3).run(test_suite())

