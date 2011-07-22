from odin.ecmwf.ecmwf_nc import Ecmwf_Grib2
from odin.config.environment import config,set_hermod_logging
from odin.config.database import connect
from os.path import join,basename
from glob import glob
import logging

def create_insert():
    set_hermod_logging()
    conf = config()
    log = logging.getLogger(__name__)
    basepath = conf.get('ecmwf','spooldir')
    log.info('Scanning {0} for ECMWF gribfiles'.format(basepath))
    pattern = join(basepath,'ECMWF_ODIN_*+000H00M')
    file_list = glob(pattern)
    log.info('Found {0} new gribfiles'.format(len(file_list)))
    db = connect()
    cursor = db.cursor()
    for f in file_list:
        ecmwf = Ecmwf_Grib2(f)
        ecmwf.convert2nc()
        ecmwf.convert2odin()
        ecmwf.cpfile()
        record = {}
        record['date'] = ecmwf.time.date()
        record['type'] = 'AN'
        record['hour'] = ecmwf.time.hour
        record['filename'] = ecmwf.outfile().split(
                conf.get('ecmwf','basedir'))[1]
        cursor.execute("""
                replace ecmwf (date,type,hour,filename) 
                values (%(date)s, %(type)s, %(hour)s, %(filename)s)
                """ , (record))
        ecmwf.delete()
        log.info('processed file {0}'.format(ecmwf.outfile()))
    cursor.close()
    db.close()
	
