import datetime as DT
from sys import argv, exit
import numpy as np
import odin.ecmwf.NC4ecmwf as NC
from scipy.integrate import odeint
from scipy.interpolate import splmake, spleval, spline
from scipy import io as sio
from pylab import diff, interp
from pkg_resources import resource_filename
from os.path import join
from odin.config.environment import set_hermod_logging, config
import logging
class ZptFile(dict):
    '''
         Create ZPT2 file using the new NetCDF ECMWF files
         Created
             Donal Murtagh July 2011.

    '''

    def donaletty(self, g5zpt, month, day, newz, lat):
        '''Inputs :
                    g5zpt : heights (km) Pressure (hPa) and temperature profile
                            should extend to at least 60 km
                    month : month of observation
                    day : day of month of observation
                    lat : latitude of observation
            Output : ZPT array [3, 0-120]
        '''
        def intatm(z, T, newz, normz, normrho, lat):
            ''' Integrates the temperature profile to yield a new model atmosphere
            in hydrostatic equilibrium including the effect of g(z) and M(z)
            newT,p,rho,nodens,n2,o2,o= intatm(z,T,newz,normz,normrho)
            NOTE z in km and returns pressure in pa
            '''
            wn2 = 0.78084 # mixing ratio N2
            wo2 = 0.209476 #mixing ratio O2
            Ro = 8.3143 # ideal gas constant
            k = 1.38054e-23 # jK-1 Boltzmans constant
            m0 = 28.9644
            def geoid_radius(latitude):
                '''
                Function from GEOS5 class.
                GEOID_RADIUS calculates the radius of the geoid at the given latitude
                [Re] = geoid_radius(latitude) calculates the radius of the geoid (km)
                at the given latitude (degrees).
                ----------------------------------------------------------------
                       Craig Haley 11-06-04
                ---------------------------------------------------------------
                '''
                DEGREE = np.pi / 180.0
                EQRAD = 6378.14 * 1000
                FLAT = 1.0 / 298.257
                Rmax = EQRAD
                Rmin = Rmax * (1.0 - FLAT)
                Re = np.sqrt(1./(np.cos(latitude*DEGREE)**2/Rmax**2
                              + np.sin(latitude*DEGREE)**2/Rmin**2)) / 1000
                return Re


            def intermbar(z):
                Mbars = np.r_[28.9644, 28.9151, 28.73, 28.40, 27.88, 27.27, 26.68, 26.20, 25.80, 25.44, 25.09, 24.75, 24.42, 24.10]
                Mbarz=np.arange(85,151,5)
                m=interp(z,Mbarz,Mbars)
                return m

            def g(z, lat):
                #Re=6372;
                #g=9.81*(1-2.*z/Re)
                return 9.80616 *(1 - 0.0026373*np.cos(2*lat*np.pi/180.) + \
                             0.0000059*np.cos(2*lat*np.pi/180.)**2)*(1-2.*z/geoid_radius(lat))

            def func(y,z,xk,cval,k):
                grad=spleval((xk,cval,k),z)
                return grad

            newT=spline(z,T,newz)
            mbar_over_m0=intermbar(newz)/m0
            splinecoeff=splmake(newz,g(newz,lat)/newT*mbar_over_m0,3)
            integral=odeint(func,0,newz,splinecoeff)
            integral=3.483*np.squeeze(integral.transpose())
            integral=(1*newT[1]/newT*mbar_over_m0*np.exp(-integral))
            normfactor=normrho/spline(newz,integral,normz)
            rho=normfactor*integral
            nodens=rho/intermbar(newz)*6.02282e23/1e3
            n2=wn2*mbar_over_m0*nodens
            o2=nodens*(mbar_over_m0*(1+wo2)-1)
            o=2*(1-mbar_over_m0)*nodens
            o[o<0]=0
            p=nodens*1e6*k*newT
            return newT,p,rho,nodens,n2,o2,o


        Ro=8.3143 # ideal gas constant
        k=1.38054e-23 # jK-1 Boltzman's constant
        #load cira.mat
        cira = sio.loadmat(resource_filename('odin.ecmwf','cira.mat'))
        latpt=np.min([np.max([1,round((lat+85)/10+0.5)]),17])
        monthrange=np.arange((month-1)*25,month*25)
        ciraT=cira['temp'][monthrange,latpt]
        z=np.r_[g5zpt[g5zpt[:,0]<60,0],np.arange(75,121,5)]
        temp=np.r_[g5zpt[g5zpt[:,0]<60,2],ciraT[15:25]]
        newz=np.arange(121)
        normrho=interp([20],g5zpt[:,0],g5zpt[:,1])*28.9644/1000/Ro/interp([20],
                       g5zpt[:,0],g5zpt[:,2])
        newT,newp,rho,nodens,n2,o2,o=intatm(z,temp,newz,20,normrho[0],lat)
        zpt=np.vstack((newz,newp,newT)).transpose()
        return zpt



    def __init__(self, filename, outputfilename):
        self.conf = config()
        self.log = logging.getLogger(__name__)
        self.log.info('Creating ptz-file for {0}'.format(filename))
        ecmz = np.arange(65)
        newz = np.arange(121)

        def mjd2utc(MJD):
            dateoffset = (DT.date(2001, 1, 1).toordinal())-51910
            return DT.datetime.fromordinal(
                int(MJD)+dateoffset)+DT.timedelta(MJD-int(MJD))

        def utc2mjd(year, month, day, hour=0, min=0, sec=0, ticks=0):
            deltat = DT.timedelta(0, (hour*60 + min)*60+ sec, ticks)
            dateoffset = (DT.date(2001, 1, 1).toordinal())-51910
            return (
                DT.date(year, month, day).toordinal()-dateoffset+(
                    deltat.seconds + deltat.microseconds/1e6
                    )/24./60./60.)

        def readlogfile(filename):
            logfile = open(filename, 'r')
            allrows = logfile.readlines()
            nrows = np.size(allrows)
            data = np.zeros((nrows, 12))
            for row in range(nrows):
                tmp = allrows[row].split()
                data[row] = np.r_[tmp[0:12]]
            return data

        self.filename = filename
        fid = open(outputfilename, 'w')
        logdata = readlogfile(self.filename)
        logdata[logdata[:, 5] > 180, 5] -= 360.0 #fixa longituder till -180-180
        fid.write('# ARRAY dimension (={0})\n'.format(logdata.shape[0]))
        fid.write('# MATRIX dimensions (always 3 columns)\n')
        fid.write('# Pressure[hPa] Temperature[K] Altitude[km]\n')
        fid.write('# Created the script hermodcreateptz in the odin.ecmwf package\n')
        fid.write('{0}\n'.format(logdata.shape[0]))
        log_datetime = mjd2utc(logdata[0, 11])
        #all values are integers..
        file_hour = (log_datetime.hour+3)/6*6
        file_datetime = log_datetime.replace(hour=0)
        file_datetime += DT.timedelta(hours=file_hour)
        basepath = self.conf.get('ecmwf', 'basedir')
        ecmwffilename_template = join(
            basepath,
            '%Y', '%m', 'ODIN_NWP_%Y_%m_%d_%H.NC')
        ecmwffilename = file_datetime.strftime(ecmwffilename_template)
        self.log.info('Using ECMWF file: {0}'.format(ecmwffilename))
        ecm = NC.NCecmwf(ecmwffilename)
        minlat = np.min(ecm['lats'])
        latstep = np.mean(diff(ecm['lats']))
        minlon = np.min(ecm['lons'])
        lonstep = np.mean(np.diff(ecm['lons']))
        for i in np.arange(logdata.shape[0]):
            #extract T and P for the starting lat and long of each scan
            #(Should be updated to middle but needs a good way of averaging
            #the start and end longitutudes)
            latpt = np.int(np.floor((logdata[i, 4]-minlat)/latstep))
            lonpt = np.int(np.floor((logdata[i, 5]-minlon)/lonstep))
            T = ecm.extractprofile_on_z('T', latpt, lonpt, ecmz*1000)
            P = ecm.extractprofile_on_z(
                'P', latpt, lonpt, ecmz*1000)/100. # to hPa
            T[np.isnan(T)] = 273.0 # tempory fix in case ECMWF make
            #temperatures below the surface nans, P shouldn't matter
            zpt = self.donaletty(
                np.c_[ecmz, P, T],
                file_datetime.month,
                file_datetime.day,
                newz,
                logdata[i, 4])
            fid.write('{0:<4}{1:<4}\n'.format(*zpt.shape))
            for row in zpt.tolist():
                fid.write('{1:.6e} {2:.6e} {0:.6e}\n'.format(*row))
        fid.close()
        self.log.info('Created {0} successfully'.format(outputfilename))

def main():
    set_hermod_logging()
    if len(argv) == 3: ## command and two arguments
        zpt = ZptFile(argv[1],argv[2])
    else:
        exit('Command uses one infile and one outfile as an argument')

if __name__ == "__main__":
    main()
