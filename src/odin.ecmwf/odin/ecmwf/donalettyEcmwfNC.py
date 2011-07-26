import datetime as DT
from sys import argv
import numpy as np
import odin.ecmwf.NC4ecmwf as NC
from scipy.integrate import odeint
from scipy.interpolate import splmake, spleval,spline
from scipy import io as sio


class ZptFile(dict):
    '''
         Create ZPT2 file using the new NetCDF ECMWF files
         Created
             Donal Murtagh July 2011.
             
    '''
    
    def donaletty(g5zpt, month, day, lat):
        '''Inputs :
                    g5zpt : heights (km) Pressure (hPa) and temperature profile
                            should extend to at least 60 km
                    month : month of observation
                    day : day of month of observation
                    lat : latitude of observation
            Output : ZPT array [3, 0-120]
        '''
        def intatm(z,T,newz,normz,normrho,lat):
            ''' Integrates the temperature profile to yield a new model atmosphere
            in hydrostatic equilibrium including the effect of g(z) and M(z)
            newT,p,rho,nodens,n2,o2,o= intatm(z,T,newz,normz,normrho)
            NOTE z in km and returns pressure in pa
            '''
            wn2=0.78084 # mixing ratio N2
            wo2=0.209476 #mixing ratio O2
            Ro=8.3143 # ideal gas constant
            k=1.38054e-23 # jK-1 Boltzmans constant
            m0=28.9644
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
                  DEGREE = n.pi / 180.0
                  EQRAD = 6378.14 * 1000
                  FLAT = 1.0 / 298.257
                  Rmax = EQRAD
                  Rmin = Rmax * (1.0 - FLAT)
                  Re = n.sqrt(1./(n.cos(latitude*DEGREE)**2/Rmax**2
                                + n.sin(latitude*DEGREE)**2/Rmin**2)) / 1000
                  return Re


            def intermbar(z):
                Mbars = n.r_[28.9644, 28.9151, 28.73, 28.40, 27.88, 27.27, 26.68, 26.20, 25.80, 25.44, 25.09, 24.75, 24.42, 24.10]
                Mbarz=n.arange(85,151,5)
                m=interp(z,Mbarz,Mbars)
                return m    

            def g(z,lat):
                #Re=6372;  
                #g=9.81*(1-2.*z/Re)
                return 9.80616 *(1 - 0.0026373*n.cos(2*lat*n.pi/180.) + \
                             0.0000059*n.cos(2*lat*n.pi/180.)**2)*(1-2.*z/geoid_radius(lat))

            def func(y,z,xk,cval,k):
                grad=spleval((xk,cval,k),z)
                return grad

            newT=spline(z,T,newz)
            mbar_over_m0=intermbar(newz)/m0
            splinecoeff=splmake(newz,g(newz,lat)/newT*mbar_over_m0,3)
            integral=odeint(func,0,newz,splinecoeff)
            integral=3.483*n.squeeze(integral.transpose())
            integral=(1*newT[1]/newT*mbar_over_m0*n.exp(-integral))
            # print integral.shape, newz.shape    
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
        cira = sio.loadmat('cira.mat')
        latpt=min(max(1,round((lat+85)/10+0.5)),17)
        monthrange=np.arange((month-1)*25,month*25)
        ciraT=cira['temp'][monthrange,latpt]
        z=r_[g5zpt[g5zpt[:,0]<60,0],arange(75,121,5)]
        temp=r_[g5zpt[g5zpt[:,0]<60,2],ciraT[15:25]]
        newz=np.arange(121)
        normrho=interp([20],g5zpt[:,0],g5zpt[:,1])*28.9644/1000/Ro/interp([20],
                       g5zpt[:,0],g5zpt[:,2])
        newT,newp,rho,nodens,n2,o2,o=intatm(z,temp,newz,20,normrho[0],lat)
        zpt=np.vstack((newz,newp,newT)).transpose()
        return zpt



    def __init__(self, filename, outputfilename):
        ecmwfpath='/odin/external/ecmwf/'
        ecmz=np.arange(65)
        newz=np.arange(121)
    
        def mjd2utc(MJD):
            dateoffset=(DT.date(2001,1,1).toordinal())-51910
            return DT.datetime.fromordinal(int(MJD)+dateoffset)+DT.timedelta(MJD-int(MJD))

        def utc2mjd(year, month, day, hour=0, min=0, sec=0, ticks=0):
            deltat=DT.timedelta(0, (hour*60 + min)*60+ sec , ticks)
            return(DT.date(year,month,day).toordinal()-dateoffset+(deltat.seconds + deltat.microseconds/1e6)/24./60./60.)

        def readlogfile(filename):
            f=file(filename,'r')
            allrows=f.readlines()
            nrows=np.size(allrows)
            data=np.zeros((nrows,12))
            for row in range(nrows):
                tmp=allrows[row].split()    
                data[row]=np.r_[tmp[0:12]]    
            return data
        
        self.filename=filename
        fid=open(outputfilename,'aw')
        logdata=readlogfile(self.filename)
        np.array(logdata.shape[0]).tofile(fid,' ','%3d')
        np.array(newz.shape[0]).tofile(fid,' ','%3d')
        newz.tofile(fid,' ', '%5.2f\n')
        datetime=mjd2utc(logdata[0,11])
        hourstr=str(np.int(datetime.hour/6)*600)
        ecmwffilename=ecmwfpath+'ODIN_'+datetime.strftime('%Y%m%d')+'-AN-91-22.NC'
        print 'Using ECMWF file : '+ecmwffilename
        ecm=NC.NCecmwf(ecmwffilename)
        minlat=np.min(ecm['lats'])
        latstep=np.mean(diff(ecm['lats']))
        minlon=np.min(ecm['lons'])
        lonstep=np.mean(np.diff(ecm['lons']))
        for i in np.range(logdata.shape[0]):
            #extract T and P for the starting lat and long of each scan (Should be updated to middle but needs a good way of averaging the start and end longitutudes) 
            latpt=np.int(np.floor((logdata[i,4]-minlat)/latstep))
            lonpt=np.int(np.floor((logdata[i,5]-minlon)/lonstep))
            T=extractprofile_on_z(self,'T',latpt,lonpt,ecmz)
            P=extractprofile_on_z(self,'P',latpt,lonpt,ecmz)/100. # to hPa
            T[np.isnan(T)]=273.0 # tempory fix in case ECMWF make temperatures below the surface nans, P shouldn't matter
            zpt=donaletty(np.c_[ecmz,P,T],datetime.month(),datetime.day(),newz)
            zpt[1:2,:].tofile(fid,' ','%5.1f %6.4e\n')
        fid.close()
            
def main(infile,outfile):
    zpt = ZptFile(infile,outfile)

if __name__=="__main__":
    main(argv[1],argv[2]) 
