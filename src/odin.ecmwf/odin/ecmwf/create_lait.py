
from odin.config.environment import config,set_hermod_logging
from odin.config.database import connect
from odin.ecmwf.pyPV2EQL import main
from os.path import join,basename,split
from glob import glob
import logging

def create_insert():
    set_hermod_logging()
    conf = config()
    log = logging.getLogger(__name__)
    basepath = conf.get('ecmwf','basedir')

    log.info('Scanning database for non existing lait-files')
    db = connect()
    cursor1 = db.cursor()
    cursor2 = db.cursor()
    cursor1.execute(
        """
        select date, hour, ecmwf.filename from ecmwf 
        left join lait using (date,hour)
        where     ecmwf.type ='AN' and lait.filename is null
        limit 480
        """ )
    for date,hour,filename in cursor1:
        try:
            main(basepath+filename)
        except Exception,msg:
            print msg
            log.error('some problems creating laitfile from {0}: {1}'.format(
                filename,msg))
            continue
        cursor2.execute(
            '''
            insert into lait (date,hour,filename) values (%s,%s,%s)
            ''',(date,hour,filename.replace('.NC','.lait.mat')))
    cursor2.close()
    cursor1.close()
    db.close()
	
