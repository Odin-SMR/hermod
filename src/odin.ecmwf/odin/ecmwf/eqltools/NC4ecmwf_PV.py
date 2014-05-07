'''
to read pv data from netcdf4
based on NC4ecmwf.py

@Auther: Kazutoshi Sagi
'''

#-----------------------------
from netCDF4 import Dataset
import numpy as np
import odin.ecmwf.GPHlib as GPH
from pylab import interp
#-----------------------------

class NC4:
	
	def __init__(self,filename):
		'''
		
		'''
		self.file = filename
		
		fid=Dataset(filename, 'r')
		self.fid = fid
		
		groups = fid.groups.keys()
		groupnames = {}
		for gr in groups:
			vars = fid.groups[gr].variables.keys()
			for v in vars:
				groupnames[v] = []
				groupnames[v].append(gr)
		self.groupnames = groupnames
		
		lats = fid.groups['Geolocation'].variables['lat']
		lats = np.r_[lats]
		self.latsort = lats.argsort()
		self.lats = lats[self.latsort]
		
		lons = fid.groups['Geolocation'].variables['lon']
		#change longitudes from  0- 360 to -180 - 180
		lons = np.r_[lons]
		lons[lons>180] = lons[lons>180]-360
		self.lonsort = lons.argsort()
		self.lons = lons[self.lonsort]
		
		self.theta = self.readfield('PT',self.latsort,self.lonsort)
		self.pv0 = self.readfield('PV',self.latsort,self.lonsort)

	def readfield(self,fieldname,latsort,lonsort):
		field = self.fid.groups[self.groupnames[fieldname][0]].variables[fieldname]
		field = np.ma.filled(field,np.nan)
		field = field[:,latsort,:] #sort by latitude
		field = field[:,:,lonsort] #sort by longitude
		return field
	
	def convert_on_theta(self,thlevels):
		'''
		return converted PV on selected PT surfaces
		'''
		#get the pressures on the model levels
		theta=self.theta
		
		mask = self.pv0==-999
		#mask = self.mkmask()
		pv0 = np.ma.masked_array(self.pv0,mask,fill_value=-999).filled()
		pv = np.zeros((len(thlevels),len(self.lats),len(self.lons)))
		
		for i in range(len(self.lats)):
			for j in range(len(self.lons)):
				#newfield[:,i,j]=np.interp(np.log(plevels),np.flipud(logpres[:,i,j]),np.flipud(field[:,i,j]))
				i_theta = np.argsort(theta[:,i,j])
				theta0 = theta[i_theta,i,j]
				pv00 = pv0[i_theta,i,j]
				pv[:,i,j]=np.interp(thlevels,theta0[pv00!=-999],pv00[pv00!=-999])
		
		return pv
	
	def mkmask(self):
		mask = np.zeros([self.theta.shape[0],self.theta.size/self.theta.shape[0]])
		
		for i in range(self.theta.shape[0]):
			a = self.pv0[i].ravel()
			b = smooth(a,1024)
			id = np.logical_or((a>2*a.std()+b),(a<-2*a.std()+b))
			mask[i,id] = 1
		
		mask = mask.reshape(self.theta.shape)
		return mask


def smooth(f, window_len=10, window='hanning'):
    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        f: the input signal 
        window_len: the dimension of the smoothing window
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    t = np.linspace(-2,2,0.1)
    x = np.sin(t)+np.random.randn(len(t))*0.1
    y = smooth(x)
    
    see also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string   
    """

    if f.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if f.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."

    if window_len < 3:
        return f

    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"

    s=np.r_[2*f[0]-f[window_len:1:-1], f, 2*f[-1]-f[-1:-window_len:-1]]
    
    if window == 'flat': #moving average
        w = np.ones(window_len,'d')
    else:
        w = getattr(np, window)(window_len)
    y = np.convolve(w/w.sum(), s, mode='same')
    return y[window_len-1:-window_len+1]
