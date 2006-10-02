from scipy import *
from numpy import *


from pyhdf.HDF import *
from pyhdf.VS import *

import pylab

import sys 
import MySQLdb
import glob

HEIGHT_BINS = 50
LAT_BINS = 45
class SMRLevel2:
   
    def __init__(self,files):
        self.hdffiles = files
        self.species = set()
        self.profiles = dict()
        self.readl2()

    def readl2(self):
        """
        Reads a the associated hdf file. Returns a list of dictionaries. If an error occurs it returns an empty list.
        """
        geolocation = []
        retrieval = []
        data = []

        for hdffile in self.hdffiles:
            try:
                f = HDF(hdffile)
                vs = f.vstart()
                
                vd = vs.attach("Geolocation")
                index = vd.inquire()[2]
                g = [ dict(zip(index,d)) for d in vd[:] ]
                vd.detach()

                vd = vs.attach("Retrieval")
                index = vd.inquire()[2]
                r = [ dict(zip(index,d)) for d in vd[:] ]
                vd.detach()

                vd = vs.attach("Data")
                index = vd.inquire()[2]
                d = [ dict(zip(index,d)) for d in vd[:] ]
                vd.detach()
            
                vs.end()
                f.close()
            except HDF4Error:
                mesg = "error reading %s\n" % hdffile
                sys.stderr.write(mesg)
                exit

            for a in r:
                self.species.add( a['SpeciesNames']  )
                prof = [ i for i in d if i['ID2']==a['ID2']]
                for i in g:
                    if i['ID1'] == a['ID1']:
                        geol = i
                type = a['SpeciesNames']
                if type not in self.profiles.keys():
                    print "adding %s" % type
                    self.profiles[type]=[]
                self.profiles[type].append(profile(type,prof,geol))
    
    def zonalmean(self):
        for i in self.species:
            #bin profiles
            map = empty((len(self.profiles[i]),LAT_BINS,HEIGHT_BINS))
            map.fill(nan)
            lats = array([j.geo['Latitude'] for j in self.profiles[i]])
            bins = digitize(lats,linspace(-90,90,LAT_BINS))
            for j,v in enumerate(bins):
                map[j,v] = self.profiles[i][j].profile
            print map.shape
            print nansum(map,axis=0).shape
            
            pylab.axis([-90,90,5,100])
            pylab.imshow(pylab.array(nansum(map,axis=0).tolist()))

            pylab.title(i)
            pylab.show()
                    


    def plot(self):
        altitude = linspace(5,LAT_BINS,HEIGHT_BINS)
        data = dict().fromkeys(self.species)
        for i in self.species:
            profiles = []
            for a in self.profiles[i]:
                profiles.append(a.profile)
            data[i]=vstack(tuple(profiles))
            mask = isnan(data[i])
            data[i].putmask([0],mask)
            pylab.plot(sum(data[i],axis=0))
            pylab.title(i)
            pylab.show()
            pylab.imshow(pylab.array(data[i].tolist()))
            pylab.title(i)
            pylab.show()


class profile:
    """
    This class contains one profile of a certain species
    """
    def __init__(self,type,data,geo):
        self.species = type
        self.data = data
        self.geo = geo
        self.interpol()

    def interpol(self):
        alt =  array([a['Altitudes'] for a in self.data])
        prof = array([a['Profiles'] for a in self.data])
        resp = array([a['MeasResp'] for a in self.data])

        mask = resp > .8
        profiles = prof[mask]
        altitudes = alt[mask]

        self.altitude = linspace(5,100,HEIGHT_BINS)
        if len(profiles)>2:
            pr = interpolate.interp1d(altitudes,profiles,bounds_error=0)

            self.profile = pr(self.altitude)
        else:
            self.profile = empty(len(self.altitude))
            self.profile.fill(nan)

    def plot(self):
        mask2 = isfinite(self.profile)
        p = self.profile[mask2]
        a = self.altitude[mask2]

        plot(p,a)
        title(self.species)
        show()


class verifyDatabaseAndDisk:
    """
    Verify contents in the level2 database and ensure that files on disk exists as the database believe
    """
    def __init__(self):
        pass

    def verify(self):
        db = MySQLdb.connect(host="jet",user="odinuser",passwd="***REMOVED***",db="odin")
        c=db.cursor(MySQLdb.cursors.DictCursor)
        status=c.execute ("""select distinct orbit,scans.freqmode ,calibration,version,level2.fqid,name,midfreq,l2prefix from scans natural join level2 natural join Freqmodes""")
        for row in c:
            file =  "/odin/smr/Data/SMRl2/SMRhdf/Qsmr-%s/%s/SCH_%s_%s%0.4X_%s.L2P" % (row['version'],row['name'],row['midfreq'],row['l2prefix'],row['orbit'],"".join(row['version'].split("-")).zfill(3))
            if not self.test(file):
                print file

    def test(self,f):
        """
        Is the file f there?
        """
        try:
            fh = open(f)
            fh.close()
        except IOError:
            return False
        return True


def main():
    files = glob.glob('*.L2P')
    #files = ['SCH_5018_C54EB_021.L2P']
    x = SMRLevel2(files)
    print len(x.profiles)
    x.zonalmean()

if __name__ == "__main__":
    main()
