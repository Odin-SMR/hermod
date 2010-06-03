import unittest
from odin.config.environment import config,HermodError,HermodWarning
from odin.config.database import connect

class DatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.con = connect()

    def tearDown(self):
        self.con.close()

    def opendb(self):
        pass

    def database(self):
       cur = self.con.cursor()
       cur.execute('''select * from statusl2 order by date limit 10;''')
       res =cur.fetchall()
       cur.close()
       self.assertEqual(len(res),10)


def test_suite():
    tests = [
            'opendb',
            'database',
            ]
    return unittest.TestSuite(map(DatabaseTestCase,tests))

if __name__=='__main__':
    unittest.TextTestRunner(verbosity=3).run(test_suite())

