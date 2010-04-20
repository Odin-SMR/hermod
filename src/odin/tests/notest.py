import unittest

class NoTestCase(unittest.TestCase):

    def test1(self):
        self.assertEqual(1,1);

    def testT(self):
        self.assertTrue(True);


def test_suite():
    tests = [
            'test1',
            'testT',
            ]
    return unittest.TestSuite(map(NoTestCase,tests))

if __name__=='__main__':
    unittest.TextTestRunner(verbosity=2).run(test_suite())

