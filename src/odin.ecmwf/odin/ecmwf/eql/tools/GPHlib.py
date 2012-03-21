import numpy as n

def geopotential2geometric(H,latitude):
		'''
		GEOPOTENTIAL2GEOMETRIC Converts geopoential height to geometric height
		[Z] = geopotential2geometric(H, latitude) converts the given
		geopotential height (km) to geometric height (km) above the reference ellipsoid
		at the given latitude (degrees).
		- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
		Craig Haley 11 - 06 - 04
		15 - 06 - 04 CSH modified to work with H vector by scalar lat
		 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

		if ((H.size > 1) & (latitude.size ==1)):
			latitude = latitude * n.ones(n.size(H))
		'''   
		DEGREE = n.pi / 180.0
		g0 = 9.80665
		g = 9.80616 *(1 - 0.002637*n.cos(2*latitude*DEGREE) + 0.0000059*n.cos(2*latitude*DEGREE)**2)
		G= g / g0
		Re = geoid_radius(latitude) * 1000
		'''
		This is an attempt to allow several latitude dimentions
		if n.ndim(H)==1: H=n.reshape(H,(1,-1))
		Re=n.reshape(Re,(1,-1))
		G=n.reshape(G,(1,-1))
		Z = n.dot(H.T,Re)/(n.repeat((G*Re),H.size,axis=0)- n.repeat(H.T,G.size,axis=1) * 1000);
		'''
		Z=H*Re/(G*Re-H*1000)
		return Z

def geoid_radius(latitude):
		''' GEOID_RADIUS calculates the radius of the geoid at the given latitude
		[Re] = geoid_radius(latitude) calculates the radius of the geoid (km) at the
		given latitude (degrees).

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