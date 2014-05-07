from unittest import makeSuite,TestSuite,TextTestRunner,TestCase,TestLoader

from odin.hermod.interfaces import IKerberosTicket, IGetFiles, IMatlab
from odin.hermod.interfaces import IMakeZPT, IPbs


class IKerberosTicketTestCase(TestCase):
    def setUp(self):
        self.obj = IKerberosTicket()

    def test_request(self):
        self.assertRaises(NotImplementedError,self.obj.request)

    def test_check(self):
        self.assertRaises(NotImplementedError,self.obj.check)

    def test_renew(self):
        self.assertRaises(NotImplementedError,self.obj.renew)

class IGetFilesTestCase(TestCase):
    def setUp(self):
        self.obj = IGetFiles()

    def test_connect(self):
        self.assertRaises(NotImplementedError,self.obj.connect)

    def test_get(self):
        self.assertRaises(NotImplementedError,self.obj.get,None,None)

    def test_put(self):
        self.assertRaises(NotImplementedError,self.obj.put,None,None)

    def test_close(self):
        self.assertRaises(NotImplementedError,self.obj.close)

class IMatlabTestCase(TestCase):
    def setUp(self):
        self.obj = IMatlab()

    def test_start_matlab(self):
        self.assertRaises(NotImplementedError,self.obj.start_matlab)

    def test_close_matlab(self):
        self.assertRaises(NotImplementedError,self.obj.close_matlab)

    def test_matlab_is_open(self):
        self.assertRaises(NotImplementedError,self.obj.matlab_is_open)

    def test_matlab_command(self):
        self.assertRaises(NotImplementedError,self.obj.matlab_command,None)

class IMakeZPTTestCase(TestCase):
    def setUp(self):
        self.obj = IMakeZPT()

    def test_checkIfValid(self):
        self.assertRaises(NotImplementedError,self.obj.checkIfValid)

    def test_makeZPT(self):
        self.assertRaises(NotImplementedError,self.obj.makeZPT)

class IPbsTestCase(TestCase):
    def setUp(self):
        self.obj = IPbs()

    def test_submit(self):
        self.assertRaises(NotImplementedError,self.obj.submit)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(WidgetTestCase('test_default_size'))
    suite.addTest(WidgetTestCase('test_resize'))
    return suite

def test_suite():
    suite1 = TestLoader().loadTestsFromTestCase(IKerberosTicketTestCase)
    suite2 = TestLoader().loadTestsFromTestCase(IGetFilesTestCase)
    suite3 = TestLoader().loadTestsFromTestCase(IMatlabTestCase)
    suite4 = TestLoader().loadTestsFromTestCase(IMakeZPTTestCase)
    suite5 = TestLoader().loadTestsFromTestCase(IPbsTestCase)

    return TestSuite([suite1,suite2,suite3,suite4,suite5])

if __name__=='__main__':
    TextTestRunner(verbosity=3).run(test_suite())


