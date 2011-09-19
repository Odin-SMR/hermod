import unittest
from odin.ecmwf.tests import nc_create,create_insert_test,zpt2_create_test
def additional_tests():
    return unittest.TestSuite([
        create_insert_test.test_suite(),
        nc_create.test_suite(),
        zpt2_create_test.test_suite(),
        ])

if __name__=="__main__":
    unittest.TextTestRunner(verbosity=3).run(additional_tests())

