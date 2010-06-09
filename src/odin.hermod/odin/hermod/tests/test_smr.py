
from unittest import makeSuite,TestSuite,TextTestRunner,TestCase
from odin.hermod.smr import pathdepth,filelist
class SMRTestCase(TestCase):

    def test_pathdepth(self):
	self.assertEqual(pathdepth('/'),1)
	self.assertEqual(pathdepth('/sth'),2)
	self.assertEqual(pathdepth('/sth/'),2)
	self.assertEqual(pathdepth('/sth/aoeu/aoeu/'),4)

    def test_filelist(self):
        self.assertEqual(len(filelist(6,1)),100)

def test_suite():
    tests = [
            'test_pathdepth',
            'test_filelist',
            ]
    return TestSuite(map(SMRTestCase,tests))

if __name__=='__main__':
    TextTestRunner(verbosity=3).run(test_suite())


