#from scipy import *
from numpy import *

from pyhdf.HDF import *
from pyhdf.VS import *

import pylab as p
#import matplotlib.axes3d as p3
import matplotlib.toolkits.basemap as bm

import sys 
import MySQLdb
import glob
UPPER_LIMIT=80 #km
LOWER_LIMIT=5 #km
HEIGHT_BINS = 10
LAT_BINS = 10
LONG_BINS = 20
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
            map = zeros((LAT_BINS,HEIGHT_BINS),dtype=float)
            count = zeros((LAT_BINS,HEIGHT_BINS),dtype=int)
            lats = array([j.geo['Latitude'] for j in self.profiles[i]])
            bins = digitize(lats,linspace(-90,90,LAT_BINS))

            # fill bins, count when a value is added to a bin
            for j,v in enumerate(bins):
                map[int(v),:]= map[int(v),:] + nan_to_num(self.profiles[i][j].profile)
                count[int(v),:] = count[int(v),:] + where(isfinite(self.profiles[i][j].profile),ones(HEIGHT_BINS),zeros(HEIGHT_BINS))

            # Calculate mean, Remove negative values
            z = nan_to_num(map/count)
            z[z<0] = 0.0
            zonalmean = z

            #draw plot
            p.figure()
            C = p.contourf(linspace(-90,90,LAT_BINS),linspace(LOWER_LIMIT,UPPER_LIMIT,HEIGHT_BINS),nan_to_num(zonalmean).transpose(),20)
            p.colorbar()
            p.title(i)
            p.xlabel('latitude (deg)')
            p.ylabel('altitude (km)')
            figfile = '%s.png' % i.split()[0]
            p.savefig(figfile)

    def globalplot(self):
        for i in self.species:
            #bin profiles
            maps = zeros((LAT_BINS,LONG_BINS,HEIGHT_BINS),dtype=float)
            count = zeros((LAT_BINS,LONG_BINS,HEIGHT_BINS),dtype=int)
            lats = array([j.geo['Latitude'] for j in self.profiles[i]])
            longs = array([j.geo['Longitude'] for j in self.profiles[i]])
            lat_bins = digitize(lats,linspace(-90,90,LAT_BINS))
            long_bins = digitize(longs,linspace(-180,180,LONG_BINS))
            
            #fill bins
            for j,v in enumerate(zip(lat_bins,long_bins)):
                la,lo =map(int,v)
                maps[la,lo,:] = maps[la,lo,:] + nan_to_num(self.profiles[i][j].profile)
                count[la,lo,:] = count[la,lo,:] + where(isfinite(self.profiles[i][j].profile),ones(HEIGHT_BINS),zeros(HEIGHT_BINS))




            # Calculate mean, Remove negative values
            z = nan_to_num(maps/count)
            z[z<0] = 0.0
            globalmean = z
            
            #plot
            fig = p.figure()
            m = bm.Basemap(llcrnrlon=-180.,llcrnrlat=-90.,urcrnrlon=180.,urcrnrlat=90.,resolution='c',area_thresh=10000.,projection='cyl')
            x,y = m(linspace(-180,180,LONG_BINS),linspace(-90,90,LAT_BINS))
            m.drawcoastlines()
            cs = m.contour(x,y,p.randn(LAT_BINS,LONG_BINS))
            #p.imshow(nan_to_num(globalmean[:,:,5]).transpose(),extent=[-180,180,-90,90])
            #p.colorbar()
            #p.title(i)
            #p.ylabel('altitude (km)')
            figfile = '%s.png' % i.split()[0]
            p.savefig(figfile)

           


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

        self.altitude = linspace(LOWER_LIMIT,UPPER_LIMIT,HEIGHT_BINS)
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
        db = MySQLdb.connect(host=config.get('WRITE_SQL','host'), user=config.get('WRITE_SQL','user'), passwd=config.get('WRITE_SQL','passwd'), db=config.get('WRITE_SQL','db'))
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
    files = glob.glob('*54*.L2P')
    #files = ['SCH_5018_C54EB_021.L2P']
    x = SMRLevel2(files)
    #x.zonalmean()
    x.globalplot()
if __name__ == "__main__":
    main()
