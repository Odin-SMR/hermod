from odin.ecmwf.ecmwf_nc import Ecmwf_Grib2
from odin.config.environment import config
from odin.config.database import connect
from os.path import join
from glob import glob

def create_insert():
    conf = config()
    basepath = conf.get('ecmwf','spooldir')
    pattern = join(basepath,'ECMWF_ODIN_*+000H00M')
    file_list = glob(pattern)
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
