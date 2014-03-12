import mocker
from unittest import makeSuite,TestSuite,TextTestRunner
from odin.config.environment import config
import sys
from odin.hermod.pbs import GEMPbs,runscript
from StringIO import StringIO



class PbsTestCase(mocker.MockerTestCase):

    def setUp(self):
        self.old_stdout = sys.stdout
        sys.stdout = StringIO()

    def tearDown(self):
        sys.stdout = self.old_stdout


    def test_config(self):
        "Testing configfiles"
        conf = self.mocker.mock()
        conf.get('pbs','batch_command')
        self.mocker.result("/bin/cat")

        cfg = self.mocker.replace("odin.config.environment.config")
        cfg()
        self.mocker.result(conf)

        self.mocker.replay()
        c = config()
        self.assertEqual('/bin/cat',c.get('pbs','batch_command'))

    def test_submit(self):
        "test to submit a fake job"

        conf = self.mocker.mock()
        conf.get('pbs','batch_command')
        self.mocker.result("/bin/cat")

        cfg = self.mocker.replace("odin.config.environment.config")
        cfg()
        self.mocker.result(conf)

        self.mocker.replay()

        class Fake(GEMPbs):
            pass

        a = Fake()
        a.info = {
                'id':1,
                'orbit': 1,
                'backend':'ACn',
                'name':'XXACn_a',
                'calversion': 1,
                'fqid': 1,
                'version': '2-8',
                'process_time':'00:00:10',
                }
        a.set_submit_info()
        a.submit()
        self.assertEqual(sys.stdout.getvalue().strip(),str(runscript%a.info).strip())





def test_suite():
    tests = [
            'test_config',
            'test_submit',
            ]
    return TestSuite(map(PbsTestCase,tests))

if __name__=='__main__':
    TextTestRunner(verbosity=3).run(test_suite())


