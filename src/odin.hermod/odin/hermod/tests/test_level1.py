
from unittest import makeSuite,TestSuite,TextTestRunner
from odin.hermod.level1 import Level1b
import mocker

class Level1bTestCase(mocker.MockerTestCase):

    def ecmwf_make_zpt(self):
        "Creating a level1b object"

        l1b = Levl1b()


def test_suite():
    tests = [
            'Level1bTestCase',
            ]
    return TestSuite(map(Level1bTestCase,tests))

if __name__=='__main__':
    TextTestRunner(verbosity=3).run(test_suite())


