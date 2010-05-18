
from unittest import TestCase,makeSuite,TestSuite,TextTestRunner
from odin.hermod.pdc import PDCKerberosTicket,PDCkftpGetFiles
from odin.config.environment import config
from os.path import exists,basename,join
from os import remove
from tempfile import NamedTemporaryFile

class PDCTestCase(TestCase):
    def setUp(self):
        self.config = config()
        self.pdc = PDCKerberosTicket()
        self.ftp = PDCkftpGetFiles()


    def have_configs(self):
        """checking pdc config entries.
        """
        self.assert_(self.config.has_option('PDC','passwd'))
        self.assert_(self.config.has_option('PDC','principal'))
        self.assert_(self.config.has_option('PDC','host'))
        self.assert_(self.config.has_option('PDC','smrl2_dir'))
        self.assertTrue(self.config.has_option('PDC','user'))

    def tickets(self):
        """Getting kerberostickets.
        """
        self.pdc.destroy()
        self.failIf(self.pdc.check())
        self.assert_(self.pdc.request())
        self.assert_(self.pdc.check())
        self.assert_(self.pdc.renew())
        self.pdc.destroy()
        self.failIf(self.pdc.renew())

    def filetransfers(self):
        """do a filetransfer to pdc.
        
        creates a localfile
        sends it to pdc
        get it back
        compare files
        """
        if not self.pdc.check():
            self.pdc.request()
        f = NamedTemporaryFile()
        f.write("testfile")
        f.flush()
        origfile = f.name
        remotefile = join(self.config.get('PDC','smrl2_dir'),
                'version_1.2',basename(f.name))
        localfile = basename(f.name)
        self.assert_(self.ftp.connect())
        self.assert_(self.ftp.put(origfile,remotefile))
        self.assert_(self.ftp.get(remotefile,localfile))
        self.assert_(self.ftp.delete(remotefile))
        self.assert_(self.ftp.close())
        self.assert_(self.pdc.destroy())
        cp = open(localfile)
        f.seek(0)
        self.assertEqual(f.read(),cp.read())
        cp.close()
        remove(localfile)
        f.close()
        


def test_suite():
    tests = [
            'have_configs',
            'tickets',
            'filetransfers',
            ]
    return TestSuite(map(PDCTestCase,tests))

if __name__=='__main__':
    TextTestRunner(verbosity=3).run(test_suite())


