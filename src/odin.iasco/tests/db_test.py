from unittest import TestCase,makeSuite,TestSuite

from MySQLdb import connect

from odin.hermod.hermodBase import config_files,config,connection_str


class TestConfig(TestCase):
    def SetUp(self):
        pass

    def testConfig(self):
        self.assert_(config_files!=[])
        pass
    
    def testConfigSections(self):
        self.assert_(config.sections()!=[])
        
    def testDBvar(self):
        self.assert_(config.has_section('SQL') 
                     and (config.has_section('WRITE_SQL') 
                          or config.has_section('READ_SQL')))
    
    def tearDown(self):
        pass
    
class TestSQL(TestCase):
    def setUp(self):
        self.db = connect(**connection_str)
        
    
    def testOpen(self):
        self.assert_(self.db.open==1)
        
    def tearDown(self):
        self.db.close()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestConfig))
    return suite
