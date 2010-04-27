import unittest
import mocker
import odin.iasco.db_calls
import logging
import logging.config
import datetime

def getexcept(e):
    raise e

class dbcallsTestCase(mocker.MockerTestCase):
    def setUp(self):
        pass

    def w2iasco_test(self):
	"""Testing w2iasco

	"""

	logconf = self.mocker.replace("logging.config.fileConfig")
        logconf(mocker.ANY)
        self.mocker.result(None)

	logmock = self.mocker.mock()
        logmock.info(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(None)
        #self.mocker.count(10)

        logger = self.mocker.replace("logging.getLogger")
        logger(mocker.ANY)
        self.mocker.result(logmock)
	self.mocker.count(2)

	ch = self.mocker.mock()
        ch.execute(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(2)
	self.mocker.count(2)
	ch.close()
	self.mocker.result(None)
	self.mocker.count(2)

	db = self.mocker.mock()
        db.cursor(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(ch)
        self.mocker.count(2)

        dbconnect = self.mocker.replace("MySQLdb.connect")
        dbconnect(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(db)

        self.mocker.replay()
        self.assertEquals(odin.iasco.db_calls.w2iasco(datetime.date(2010,1,1),29,'2-1'),None)
	self.mocker.verify()

    def w2iasco_orbits_test(self):
	"""Testing w2iasco_orbits

	"""
	d = self.mocker.mock()
        d.execute(mocker.ARGS,mocker.KWARGS)
	self.mocker.result(None)
	self.mocker.count(2)
        d.close()
	self.mocker.result(None)
        self.mocker.count(2)

      	db = self.mocker.mock()
        db.cursor(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(d)
        self.mocker.count(2)

        dbconnect = self.mocker.replace("MySQLdb.connect")
        dbconnect(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(db)

       	self.mocker.replay()
        self.assertEquals(odin.iasco.db_calls.w2iasco_orbits(datetime.date(2010,1,1),68317,[134982]),None)
        self.mocker.verify()


    def getStartDate_test(self):
	"""Testing getStartDate
	
	"""
	curs = self.mocker.replace("MySQLdb.cursors.DictCursor")
        curs(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(None)

	mi = self.mocker.mock()
        mi.execute(mocker.ARGS,mocker.KWARGS)
        #mi.iter()
        #self.mocker.result([None].__iter__())
	self.mocker.result([None])
        #self.mocker.count(2)
        mi.close()
        self.mocker.result(None)
        #self.mocker.count(2)
        #mi.iter()
        #self.mocker.result([None].__iter__())

#	def __iter__(self):
#	    return [None].__iter__()
	db = self.mocker.mock()
        db.cursor(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(mi)
        #self.mocker.count(2)

        dbconnect = self.mocker.replace("MySQLdb.connect")
        dbconnect(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(db)

        self.mocker.replay()
        self.assertEquals(odin.iasco.db_calls.getStartDate(),False)
        self.mocker.verify()


def test_suite():
    tests = [
            'w2iasco_test',
            'w2iasco_orbits_test',
	    #'getStartDate_test',
	    ]            
    return unittest.TestSuite(map(dbcallsTestCase,tests))

if __name__=='__main__':
    unittest.TextTestRunner(verbosity=3).run(test_suite())
