'''Creating wind speed files for the IASCO model'''
from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy import interpolate
from scipy.io import savemat
from mpl_toolkits.basemap import Basemap
from datetime import date, timedelta

class Windfields:
    '''a class derived for creating wind-fields 
        from ecmwf .nc file'''
    def __init__(self, ncfile):
        self.root_grp = Dataset(ncfile)

    def getdata(self, group, variable):
        '''extract variable data from .nc file'''
        group = self.root_grp.groups[group]
        data = np.array(group.variables[variable])
        return data

    def getdataforwinds(self):
        '''extract variables from .nc file'''
        self.lat = self.getdata('Geolocation', 'lat')
        self.lon = self.getdata('Geolocation', 'lon')
        self.U = self.getdata('Data_3D', 'U')
        self.V = self.getdata('Data_3D', 'V')
        self.PT = self.getdata('Data_3D', 'PT')
        #change the grids so lat is from -90 to 90 
        #and lon is from -180 to 180  
        #first latitude
        ind = np.argsort(self.lat)
        self.lat = self.lat[ind]
        self.U = self.U[:, ind, :]
        self.V = self.V[:, ind, :]
        self.PT = self.PT[:, ind, :]
        #then longitude
        self.lon[self.lon >= 180] = self.lon[self.lon >= 180]-360
        ind = np.argsort(self.lon)
        self.lon = self.lon[ind]
        self.U = self.U[:, :, ind]
        self.V = self.V[:, :, ind]
        self.PT = self.PT[:, :, ind]
      

    def pt_interpolation(self, indata1, indata2, pt):
        '''interpolates 3-d indatax to 3-d outdatax on desired pt levels'''
        outdata1 = np.zeros(shape=(pt.shape[0], self.lat.shape[0],
                                self.lon.shape[0]))
        outdata2 = np.zeros(shape=(pt.shape[0], self.lat.shape[0],
                                self.lon.shape[0]))
        for iind in range(len(self.lat)):
            for jind in range(len(self.lon)):
                x = np.array(self.PT[:, iind, jind])
                y1 = np.array(indata1[:, iind, jind])
                y2 = np.array(indata2[:, iind, jind])
                i, indices = np.unique(x, return_index=True)
                outdata1[:, iind, jind] = np.interp(pt, x[indices], y1[indices])
                outdata2[:, iind, jind] = np.interp(pt, x[indices], y2[indices])
        return outdata1, outdata2

    def geolocation_interpolation(self, data, lat, lon):
        '''interpolate data to a desired lat/lon grid'''
        f = interpolate.RectBivariateSpline(self.lat, self.lon,
                                          data, kx = 1,ky = 1,s = 0)
        outdata = f(lat, lon)
        return outdata

    def run_interpolation(self, ept, lat, lon):
        '''performs interpolation in vertical, lat, and lon dimensions'''
        Uwind = np.zeros(shape = (ept.shape[0], lat.shape[0], lon.shape[0]))
        Vwind = np.zeros(shape = (ept.shape[0], lat.shape[0], lon.shape[0]))
        Ui, Vi = self.pt_interpolation(self.U, self.V, ept)
        for eind, epti in enumerate(ept):
            Uwind[eind, :, :] = self.geolocation_interpolation(
                Ui[eind], lat, lon)
            Vwind[eind, :, :] = self.geolocation_interpolation(
                Vi[eind], lat, lon)
        return Uwind, Vwind
         

def mjd2utc(mjd):
    '''convert scalar mjd to utc'''
    datei = date(1858, 11, 17) + timedelta(days = int(mjd))
    return datei

def save_to_matlab(datadict, filename): 
    '''save datadict to matlab format'''
    savemat(filename, mdict = datadict)

def plot_data(self, lat, lon, data):
    '''plot wind speed field at a given level'''
    fig = plt.figure(figsize=(10, 8))
    fig.add_subplot(2, 1, 1)
    map = Basemap(projection='mill', lon_0 = 0,
                  llcrnrlat = -90, urcrnrlat = 90,
                  llcrnrlon = -180, urcrnrlon = 180)
    map.drawcoastlines(linewidth = 2)
    map.drawparallels(np.arange(-90, 90, 15), labels = [1, 0, 0, 0])
    map.drawmeridians(np.arange(-180, 200, 45), labels=[0, 0, 0, 1])
    X, Y = map(*np.meshgrid(lon, lat))
    map.pcolor(X, Y, data)
    plt.colorbar(orientation = 'horizontal', shrink = 0.8, aspect = 40)
    plt.show()


def create_winds(mjd):
    '''create wind fields for a given mjd by using the Windfields class''' 
    datei = mjd2utc(mjd) 
    basedir_input = '/odin/external/ecmwfNCD/'
    basedir_output = '/odin/extdata/ecmwf/tzuv/winds2/'
    times = [0, 6, 12, 18]
    ept = np.arange(400, 1001, 25)
    lat = np.arange(-90, 90.1, 1.125)
    lon = np.arange(-180, 179.9, 1.125)

    for time in times:
        tmp = [datei.year, datei.month, datei.day, time]
        filename = 'ODIN_NWP_{0}_{1:02}_{2:02}_{3:02}.NC'.format(*tmp)
        datedir = '{0:04}/{1:02}'.format(*tmp)
        fullfile = os.path.join(basedir_input, datedir, filename)
        if os.path.isfile(fullfile):
            pass
        else:
            continue

        a = Windfields(fullfile)
        a.getdataforwinds()
        Uwind, Vwind = a.run_interpolation(ept, lat, lon)
        if 0:
            plot_data(lat, lon, np.flipud(Vwind[0, :, :]))
        a.root_grp.close()
        
        for ind, epti in enumerate(ept):

            tmp = [datei.year-2000, datei.month, datei.day, time, int(epti)]
            filename = 'winds2_{0:02}{1:02}{2:02}.{3}.{4}.mat'.format(*tmp)
            datedir = '{0:02}/{1:02}'.format(*tmp)
            fullfile = os.path.join(basedir_output, datedir, filename)
            yeardir = os.path.join(basedir_output, '{0:02}'.format(*tmp))
            if not os.path.exists(yeardir):
                os.mkdir(yeardir)
            monthdir = os.path.join(basedir_output, 
                                    '{0:02}/{1:02}'.format(*tmp))
            if not os.path.exists(monthdir):
                os.mkdir(monthdir)
            datadict = {'zon_wind': np.flipud(Uwind[ind, :, :]),
                        'mer_wind': np.flipud(Vwind[ind, :, :])}
            save_to_matlab(datadict, fullfile)   


