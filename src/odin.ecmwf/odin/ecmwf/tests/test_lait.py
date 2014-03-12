import unittest
from odin.ecmwf.create_lait import create_insert

class LaitTestCase(unittest.TestCase):
    def test_lait(self):
        create_insert()

if __name__=='__main__':
    unittest.main()
