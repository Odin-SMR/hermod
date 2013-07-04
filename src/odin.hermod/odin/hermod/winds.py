from odin.hermod.session import GEMMatlab
from odin.config.database import connect
from odin.config.environment import config
from os.path import join

class WindMaker(GEMMatlab):
    
    def __init__(self,lists):
        self.lists = lists
        self.config = config()
        self.db = connect()
        self.cursor = self.db.cursor()

    def makewind(self):
        self.start_matlab()
        prefix = self.config.get('GEM','LEVEL1B_DIR')
        self.matlab_command("cd /odin/extdata/ecmwf/tz")
        for f in self.lists:
#            print f
            idn, logfile = f
            filename = join(prefix,logfile)
            print filename
            try:
                a= self.matlab_command(
                        "create_tp_ecmwf_rss2('%s')"%filename)
            except RuntimeError,e:
                #error or logmessage
                print "error",e
                print 'from matlab:',self.m_session.buf[:]
                continue
            self.register(idn,logfile.replace("LOG","ZPT"))

        self.close_matlab()

    def register(self, idn, name):
        self.cursor.execute("""
                replace level1b_gem
                (id,filename)
                values (%s,%s)
                """,(idn,name))

    def finish(self):
        self.cursor.close()
        self.db.close()


def makewinds():
    db = connect()
    cursor = db.cursor()
    cursor.execute("""
           SELECT l1g.id,l1g.filename
            from level1b_gem l1g,level1
            where l1g.id=level1.id and l1g.filename regexp ".*LOG" and level1.start_utc<"2011-05-1"
                and not exists (
                    select * from level1b_gem s 
                    where s.filename regexp ".*ZPT" 
                        and l1g.id=s.id) 
                and l1g.filename regexp "^6.*"
            """)
    result = cursor.fetchall()
    cursor.close()
    db.close()
    l1b = WindMaker(result)
    l1b.makewind()
    l1b.finish()
