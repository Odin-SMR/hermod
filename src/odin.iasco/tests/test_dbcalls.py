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
        self.mocker.result(None)

	mi = self.mocker.mock()
        mi.execute(mocker.ARGS,mocker.KWARGS)
        iter(mi)
        self.mocker.result([{'assdate': None}].__iter__())
        mi.close()
        self.mocker.result(None)

	db = self.mocker.mock()
        db.cursor(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(mi)

        dbconnect = self.mocker.replace("MySQLdb.connect")
        dbconnect(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(db)

        self.mocker.replay()
        self.assertEquals(odin.iasco.db_calls.getStartDate(),False)
        self.mocker.verify()


    def getNewDates_test(self):
        """Testing getNewDates
        
        """
        curs = self.mocker.replace("MySQLdb.cursors.DictCursor")
        self.mocker.result(None)

        la = self.mocker.mock()
        la.execute(mocker.ARGS,mocker.KWARGS)
        self.mocker.count(2)
	iter(la)
        self.mocker.result([(datetime.date(2010,1,1),datetime.date(2010,1,1))].__iter__())
        iter(la)
        self.mocker.result([(datetime.date(2010,1,3),datetime.date(2010,1,3))].__iter__())

	la.close()
        self.mocker.result(None)
	self.mocker.count(2)

        db = self.mocker.mock()
        db.cursor(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(la)
	self.mocker.count(2)

        dbconnect = self.mocker.replace("MySQLdb.connect")
        dbconnect(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(db)

        self.mocker.replay()
        self.assertEquals(odin.iasco.db_calls.getNewDates(),[datetime.date(2010, 1, 2)])
        self.mocker.verify()

    def getWindBool_test(self):
        """Testing getWindBool
        
        """
        curs = self.mocker.replace("MySQLdb.cursors.DictCursor")
        self.mocker.result(None)

        cur = self.mocker.mock()
        cur.execute(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(False)
        cur.close()
        self.mocker.result(None)

        db = self.mocker.mock()
        db.cursor(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(cur)

        dbconnect = self.mocker.replace("MySQLdb.connect")
        dbconnect(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(db)

        self.mocker.replay()
        self.assertEquals(odin.iasco.db_calls.getWindBool([],[]),False)
        self.mocker.verify()

    def getHdfBool_test(self):
        """Testing getHdfBool
        
        """ 
        curs = self.mocker.replace("MySQLdb.cursors.DictCursor")
        self.mocker.result(None)

        cur = self.mocker.mock()
        cur.execute(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(False)
        cur.close()
        self.mocker.result(None)

        db = self.mocker.mock()
        db.cursor(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(cur)

        dbconnect = self.mocker.replace("MySQLdb.connect")
        dbconnect(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(db)

        self.mocker.replay()
        self.assertEquals(odin.iasco.db_calls.getHdfBool([],[]),False)
        self.mocker.verify()

    def getAssimilateBool_test(self):
        """Testing getAssimilateBool
        
        """ 
        curs = self.mocker.replace("MySQLdb.cursors.DictCursor")
        self.mocker.result(None)
            
        cur = self.mocker.mock()
        cur.execute(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(False)
        cur.close()
        self.mocker.result(None)

        db = self.mocker.mock()
        db.cursor(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(cur)

        dbconnect = self.mocker.replace("MySQLdb.connect")
        dbconnect(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(db)

        self.mocker.replay()
        self.assertEquals(odin.iasco.db_calls.getAssimilateBool([],[]),False)
        self.mocker.verify()

    def getAssid_test(self):
        """Testing getAssid
        
        """ 
        curs = self.mocker.replace("MySQLdb.cursors.DictCursor")
        self.mocker.result(None)
            
        a_id = self.mocker.mock()
        a_id.execute(mocker.ARGS,mocker.KWARGS)
        iter(a_id)
        self.mocker.result([{'assid': None}].__iter__())

        a_id.close()
        self.mocker.result(None)

        db = self.mocker.mock()
        db.cursor(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(a_id)

        dbconnect = self.mocker.replace("MySQLdb.connect")
        dbconnect(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(db)

        self.mocker.replay()
        self.assertEquals(odin.iasco.db_calls.getAssid([],[]),[None])
        self.mocker.verify()

    def getOrbitInfo_test(self):
        """Testing getOrbitInfo
        
        """
        curs = self.mocker.replace("MySQLdb.cursors.DictCursor")
        self.mocker.result(None)

        cur = self.mocker.mock()
        cur.execute(mocker.ARGS,mocker.KWARGS)
        iter(cur)
        self.mocker.result([{'orbit': 0,'start_utc': '2010-1-1','stop_utc': '2010-1-1','id': 0}].__iter__())

        cur.close()
        self.mocker.result(None)

        db = self.mocker.mock()
        db.cursor(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(cur)

        dbconnect = self.mocker.replace("MySQLdb.connect")
        dbconnect(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(db)

        self.mocker.replay()
        self.assertEquals(odin.iasco.db_calls.getOrbitInfo([],[],[]),{'start_utc': ['2010-1-1'], 'orbit': [0], 'l1id': [0], 'stop_utc': ['2010-1-1']})
        self.mocker.verify()


def test_suite():
    tests = [
            'w2iasco_test',
            'w2iasco_orbits_test',
	    'getStartDate_test',
	    'getNewDates_test',	
	    'getWindBool_test',
	    'getHdfBool_test',
	    'getAssimilateBool_test',
	    'getAssid_test',
	    'getOrbitInfo_test',
 	    ]            
    return unittest.TestSuite(map(dbcallsTestCase,tests))

if __name__=='__main__':
    unittest.TextTestRunner(verbosity=3).run(test_suite())
