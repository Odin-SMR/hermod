import unittest
import mocker
import odin.iasco.blackbox_main
import logging
import logging.config

def getexcept(e):
    raise e

class BlackboxTestCase(mocker.MockerTestCase):
    def setUp(self):
        pass

    def noDates(self):
        logconf = self.mocker.replace("logging.config.fileConfig")
        logconf(mocker.ANY)
        self.mocker.result(None)

        logger = self.mocker.replace("logging.getLogger")
        logger(mocker.ANY)
        self.mocker.result(None) #not very useful

        popen = self.mocker.mock()
        popen.stdin.close()
        self.mocker.result(None)
        popen.wait()
        self.mocker.result(None)

        zopepopen = self.mocker.replace("subprocess.Popen")
        zopepopen(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(popen)
        
        getnewdates = self.mocker.replace("odin.iasco.db_calls.getNewDates")
        getnewdates()
        self.mocker.result([])
        startdate = self.mocker.replace("odin.iasco.db_calls.getStartDate")
        startdate()
        self.mocker.result([])

        self.mocker.replay()
        self.assertRaises(SystemExit,odin.iasco.blackbox_main.main)
        self.mocker.verify()


def test_suite():
    tests = [
            'noDates',
            ]
    return unittest.TestSuite(map(BlackboxTestCase,tests))

if __name__=='__main__':
    unittest.TextTestRunner(verbosity=3).run(test_suite())

