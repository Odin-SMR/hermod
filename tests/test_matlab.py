import unittest
#import mocker

from odin.hermod.matlab import MatlabSession
from numpy import eye,arange,ones
from numpy.random import randn

class MatlabTestCase(unittest.TestCase):

    def setUp(self):
        self.session = MatlabSession("matlab -nojvm -nodisplay")

    def tearDown(self):
        self.session.close()

    def test_runOK(self):
        command="A=ones(10);"
        string = self.session.run(command)
        self.assertEqual(string,"")

    def test_runNOK(self):
        command="A=oxnes(10);"
        string = self.session.run(command)
        self.assertNotEqual(string,"")

    def test_clear(self):
        command="clear all"
        string = self.session.run(command)
        self.assertEqual(string,"")

    def test_sytaxerror(self):
        command="""if 1,"""
        self.session.putstring('test',command)
        string = self.session.run('eval(test)')
        self.assertNotEqual(string,"")

    def test_longscript(self):
        command = """for i=1:10
                        sprintf('aoeu %i',i);
                     end"""
        string = self.session.run(command)
        self.assertEqual(string,"")

    def test_putstring(self):
        command  = """a=1:10; save('test1.mat','a')"""
        self.session.putstring('test',command)
        string = self.session.run('eval(test)')
        self.assertEqual(string,"")

    def test_getvalue(self):
        self.session.run('A=eye(10)')
        b = eye(10)
        a = self.session.getvalue('A')
        self.assertTrue((a==b).all())

    def test_getvalueX(self):
        self.session.run('A=ones(10,10,10)')
        b = ones((10,10,10))
        a = self.session.getvalue('A')
        self.assertTrue((a==b).all())

    def test_getput(self):
        a = randn(10,5,30)
        self.session.putvalue('A',a)
        b = self.session.getvalue('A')
        self.assertTrue((a==b).all())

if __name__=='__main__':
    unittest.main()

