
from unittest import TestCase,makeSuite,TestSuite,TextTestRunner
from odin.hermod.session import GEMMatlab
from os.path import exists
from os import remove

class SessionTestCase(TestCase):

    def matlab_run(self):
        "Testing matlab"
        mat = GEMMatlab()
        mat.start_matlab()
        self.assertTrue(mat.matlab_is_open())
        mat.matlab_command("a = struct()")
        mat.matlab_command("save 'testfile.mat' a")
        self.assertTrue(exists('testfile.mat'))
        remove('testfile.mat')
        mat.close_matlab()
        self.assertFalse(mat.matlab_is_open())


def test_suite():
    tests = [
            'matlab_run',
            ]
    return TestSuite(map(SessionTestCase,tests))

if __name__=='__main__':
    TextTestRunner(verbosity=3).run(test_suite())


