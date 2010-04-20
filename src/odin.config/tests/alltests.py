import unittest
from tests import notest,test_environment

def test_suite():
    return unittest.TestSuite([
        notest.suite(),
        ])

