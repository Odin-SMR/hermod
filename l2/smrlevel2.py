
from pyhdf.HDF import *
from pyhdf.VS import *

class SMRLevel2:
    
    def __init__(self,file):
        """
        The constructor that should be used
        """
        self.hdffile = file
        self.readl2()

    def readl2(self):
        """
        Reads a the associated hdf file. Returns a list of dictionaries. If an error occurs it returns an empty list.
        """
        try:
            f = HDF(self.hdffile)                # open 'inventory.hdf' in read mode
            vs = f.vstart()                 # init vdata interface
            
            vd = vs.attach("Geolocation")   # attach 'INVENTORY' in read mode
            index = vd.inquire()[2]
            self.geolocation = [ dict(zip(index,d)) for d in vd[:] ]
            vd.detach()               # "close" the vdata

            vd = vs.attach("Retrieval")   # attach 'INVENTORY' in read mode
            index = vd.inquire()[2]
            self.retrieval = [ dict(zip(index,d)) for d in vd[:] ]
            vd.detach()               # "close" the vdata

            vd = vs.attach("Data")   # attach 'INVENTORY' in read mode
            index = vd.inquire()[2]
            self.data = [ dict(zip(index,d)) for d in vd[:] ]
            vd.detach()               # "close" the vdata

            
            vs.end()                  # terminate the vdata interface
            f.close()                 # close the HDF file
        except HDF4Error:
            mesg = "error reading %s\n" % self.hdffile
            sys.stderr.write(mesg)

    def splitDataSets(self):
        self.species = set( [ a['SpeciesNames'] for a in self.retrieval] )
        for a in self.species:
            pass


class profile:
    """
    This class contains one profile of a certain species
    """
    def __init__(self,type,data,geo):
        self.species = type
        self.data = [a.update(b) for a,b in zip(data,geo)]

    
