import unittest
from odin.config.tests import test_environment,test_database

def test_suite():
    return unittest.TestSuite([
        test_environment.test_suite(),
        test_database.test_suite()
        ])

