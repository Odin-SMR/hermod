#Set path
SPOOL_DIR= "/odin/smr/Data/spool"
LEVEL1B_DIR= "/odin/smr/Data/level1b"
SMRL1B_DIR="/odin/smr/Data/SMRl1b"
SMRL2_DIR = "/odin/smr/Data/SMRl2"
PDC_DIR = "/hsm/0/projects/esrange/odin/level1b/aero/submm"

class HermodError(Exception):
    pass

def mjdtoutc(mjdnr):
    # Julian date
    jd = int(mjdnr) + 2400000.5

    # get the fraction of UTC day.
    dayfrac = mjdnr - int(mjdnr)

    # add a half
    jd0 = jd + .5

    # determin the calender
    if (jd0 < 2299161.0):
        # Julian 
        c = jd0 + 1524.0
    else:
        # Gregorian 
        b = int(((jd0 -1868216.25)/36524.25))
        c = jd0 + (b- int(b/4) + 1525.0)

    d     = int( ((c - 122.1) / 365.25) )
    e     = 365.0 * d + int(d/4)
    f     = int( ((c - e) / 30.6001) )
    day   = int( (c - e + 0.5) - int(30.6001 * f) )
    month = int( (f - 1 - 12*int(f/14)) );
    year  = int( ( d - 4715 - int((7+month)/10)) )
    hour     = int(dayfrac*24.0)
    minute      = int((dayfrac*1440.0)-int(dayfrac*1440.0/60)*60.0)
    dayfrac  = dayfrac * 86400.0
    ticks    = (dayfrac-int(dayfrac/60)*60.0)
    secs     = int(ticks)
    ticks    = ticks- secs
    ret = "%0.4i-%0.2i-%0.2i %0.2i:%0.2i:%f" %(year,month,day,hour,minute,secs+ticks)
    return ret

class files:
    from os import walk
    def __init__(self):
        self.dir = SMRL2_DIR

    def listOf(self):
        self.list = []
        for root,dirs,files in walk(self.dir):
            self.list.extend([root+'/'+a for a in files])
            
