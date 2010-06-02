import unittest
from tests import test_environment

def test_suite():
    return unittest.TestSuite([
        test_environment.test_suite(),
        ])

