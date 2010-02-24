import unittest
#import mocker

from odin.hermod.matlab import MatlabSession

class MatlabTestCase(unittest.TestCase):

    def setUp(self):
        self.session = MatlabSession()

    def tearDown(self):
        self.session.close()

    def test_nothing(self):
        self.assertEqual(1,1)

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

#    def test_sytaxerror(self):
#        command="""if 1,"""
#        string = self.session.run(command)
#        self.assertNotEqual(string,"")

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


if __name__=='__main__':
    unittest.main()

