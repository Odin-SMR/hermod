import unittest
import mocker
import odin.iasco.db_calls
#import logging
#import logging.config
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
        #self.mocker.result(None)

        logger = self.mocker.replace("logging.getLogger")
        logger(mocker.ANY)
        self.mocker.result(None) #not very useful

        popen = self.mocker.mock()
        popen.stdin.close()
        #self.mocker.result(None)
        popen.wait()
        #self.mocker.result(None)



        self.mocker.replay()
        self.assertRaises(SystemExit,odin.iasco.blackbox_main.main)
        self.mocker.verify()

    def dates(self):
	"""Testing blackbox_main with one date in new_dates and one in start_date

	Checking if the calls for function are made as many times as expected and that the array of dates is as expected.
	"""
        logconf = self.mocker.replace("logging.config.fileConfig")
        logconf(mocker.ANY)
        self.mocker.result(None)
	
	logmock = self.mocker.mock()
        logmock.info(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(None)
	self.mocker.count(10)

        logger = self.mocker.replace("logging.getLogger")
        logger(mocker.ANY)
        self.mocker.result(logmock) 

        popen = self.mocker.mock()
        popen.stdin.close()
        #self.mocker.result(None)
        popen.wait()
        #self.mocker.result(None)

        zopepopen = self.mocker.replace("subprocess.Popen")
        zopepopen(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(popen)

        getnewdates = self.mocker.replace("odin.iasco.db_calls.getNewDates")
        getnewdates()
        self.mocker.result([datetime.date(2010, 1, 4)])
        
	startdate = self.mocker.replace("odin.iasco.db_calls.getStartDate")
        startdate()
        self.mocker.result(datetime.date(2010, 1, 1))

	self.list3=[]
	self.list29=[]

	getwindbool = self.mocker.replace("odin.iasco.db_calls.getWindBool")
	getwindbool(mocker.ARGS)
	self.mocker.call(lambda date,fqid: listing(date,fqid))
	self.mocker.count(8)
	
	def listing(date,fqid):
		if fqid==3:
			self.list3.append(date)
		elif fqid==29:
			self.list29.append(date)
		return False
        
	gethdfbool = self.mocker.replace("odin.iasco.db_calls.getHdfBool")
        gethdfbool(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(False)
	self.mocker.count(8)       
 
	getassimilatebool = self.mocker.replace("odin.iasco.db_calls.getAssimilateBool")
        getassimilatebool(mocker.ARGS,mocker.KWARGS)
        self.mocker.result(False)
	self.mocker.count(8)

	extractwinds = self.mocker.replace("odin.iasco.winds.extractWinds")
        extractwinds(mocker.ARGS,mocker.KWARGS)
        self.mocker.count(1)

	copywinds = self.mocker.replace("odin.iasco.winds.copyWinds")
        copywinds(mocker.ARGS,mocker.KWARGS)
        self.mocker.count(2)

	assimilate = self.mocker.replace("odin.iasco.assimilation.assimilate")
        assimilate(mocker.ARGS,mocker.KWARGS)
        self.mocker.count(2)

	makepictures = self.mocker.replace("odin.iasco.pics.makePictures")
        makepictures(mocker.ARGS,mocker.KWARGS)
        self.mocker.count(2)

	w2iasco = self.mocker.replace("odin.iasco.db_calls.w2iasco")
        w2iasco(mocker.ARGS,mocker.KWARGS)
        self.mocker.count(2)


	self.mocker.replay()
        self.assertRaises(SystemExit,odin.iasco.blackbox_main.main)
        self.mocker.verify()
	self.assertEquals(self.list3,[datetime.date(2010,1,1), datetime.date(2010,1,2), datetime.date(2010,1,3), datetime.date(2010,1,4)])
	self.assertEquals(self.list29,[datetime.date(2010,1,1), datetime.date(2010,1,2), datetime.date(2010,1,3), datetime.date(2010,1,4)])


def test_suite():
    tests = [
            'noDates',
            'dates',
            ]
    return unittest.TestSuite(map(BlackboxTestCase,tests))

if __name__=='__main__':
    unittest.TextTestRunner(verbosity=3).run(test_suite())
