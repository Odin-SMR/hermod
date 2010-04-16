import unittest
from tests import notest

def test_suite():
    return unittest.TestSuite([
        notest.suite(),
        ])

