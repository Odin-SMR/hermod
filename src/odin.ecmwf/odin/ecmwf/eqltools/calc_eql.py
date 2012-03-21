#! /usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------

'''
calculate EQL (EQivarent Latitudes) from netcdf file.
The netcdf file generally can be found in directory "/odin/external/ecmwfNCD".

This function is based on matlab routine.
The Original routine is in odintools/ecmwf.

Created on 1 Dec, 2011
@Auther: Kazutoshi Sagi
'''
usage = "\n calc_eql.py [options] startmjd stopmjd"
__version__ = '0.1'

#------------------------------------------------------------------

import numpy as np
import odin.ecmwf.eqltools.NC4ecmwf_PV as NC4
import os
from scipy.io import savemat

pi = np.pi

#------------------------------------------------------------------

class EQL(dict):
	def __init__(self,filename,**opt):
		'''
		calculate Equivarent Latitude
		
		EQL = arcsin(A/(2pi*R**2)-1)

		where A is the area enclosed to the South
		(A = 0 corresponds to the equivalent South Pole)
		and R is the radius of the Earth.

		'''
		self.file = filename
		self.type = opt.get('type','lait') #PV converted to scaled pc according to Lait
		
		#potential temperature levels
		self.ept = np.r_[np.arange(300,725+25,25),np.arange(750,1050,50),np.arange(1250,3250,250)]
		self.ept = np.asarray(self.ept,dtype=np.double)
		#read PV values
		self.read()
		#EQL grid vector
		self.eqls = np.arange(181.) - 90
		
		#dict for output with matlab file format
		self.update({'data':{
			'pv':{
					'filename':self.file,
					'type':self.type,
					'levels':self.ept,
					'lon':self.lons,
					'lat':self.lats,
				},
			'eql':{
					'filename':self.file,
					'type':self.type,
					'levels':self.ept,
				}
		}})
		
	
	def read(self):
		'''
		read PV,longitudes and latitudes from netcdf file
		'''
		data = NC4.NC4(self.file)
		self.lons = data.lons #longitudes
		self.lats = data.lats #latitudes
		#read PV data
		self.pv = data.convert_on_theta(self.ept) #PV on selected potential temperature surface
		#scaling according to Lait et. al
		if self.type=='lait':self.pv *= (self.ept[:,np.newaxis,np.newaxis]/475.)**(-4.5)
		elif self.type=='ertel':pass
			
		self.update({'filename':os.path.abspath(self.file),'d_netcdf':data})

	def area_grid(self,R=6375.,dgrid=pi/180.):
		'''
		return grids with area of latitude from the ecmwf file
		
		Input
		-------
		R : radius (default is for the earth)
		dgrid : grid size in radians
		'''
		lats = np.deg2rad(self.lats)
		Lat = np.tile(lats,(self.lons.size,1)).T
		return (dgrid*R)**2*np.cos(Lat)
	
	def area_eql(self,R=6375.,eqls=np.arange(-90,91,1)):
		'''
		return grids with areas of equivalent latitudes defined here

		Input
		-------
		R : radius (default is for the earth)
		eqls : equivarent latitudes
		'''
		return 2*pi*R**2*(1+np.sin(np.deg2rad(eqls)))
	
	def get_eql(self):
		'''
		calculate Equivarent Latitude at each potentioal temperature surfaces
		'''
		nshape = self.pv.shape #shape of output 
		
		A_grid = self.area_grid()
		A_eql = self.area_eql()
		eql_pv_temp = np.ones([self.ept.size,self.lats.size])
		self.eql = np.ones(nshape)
		
		#use masked array of PV
		pvdata = np.ma.masked_array(self.pv,np.log10(np.abs(self.pv+1e-99))>0)
		self.mask = pvdata.mask
		
		for i_theta in range(self.ept.size):
			id = pvdata[i_theta].ravel().argsort()
			pvsort = pvdata[i_theta].ravel()[id]
			areasort = np.cumsum(A_grid.ravel()[id])
			eqvsquares = np.floor(np.interp(areasort,A_eql,range(self.eqls.size)))
			
			#ind1 = np.unique(eqvsquares,return_index=1)[1][1:-1]+1
			#eql_pv_temp[i_theta] = np.r_[1.1*pvsort[0],pvsort[ind1],1.1*pvsort[-1]]
			
			ind1 = np.arange(eqvsquares.size)[np.diff(eqvsquares)==1]
			eql_pv_temp[i_theta] = np.r_[[j.mean() for j in np.split(pvsort,ind1)]]
			
			
			tmp_eql_pv,ind2 = np.unique(eql_pv_temp[i_theta],return_index=1)
			ind3 = np.isfinite(tmp_eql_pv)
				
			if ind3.size > 175:
				self.eql[i_theta] = np.interp(pvdata[i_theta].ravel(),tmp_eql_pv[ind3],self.eqls[ind2[ind3]]).reshape(nshape[1:])
			else:
				self.eql[i_theta] *= np.nan
		
		self['data']['pv'].update({
					'data':self.pv,
					'eql':self.eql,
				})
		self['data']['eql'].update({
					'data':self.eqls[::-1],
					'pv':eql_pv_temp,
				})
	
	def saveasmat(self,filename):
		'''
		save result in matlab file with original format
		'''
		data = self['data']
		
		#change unit and shape to original
		data['pv'].update({
					'data':np.asarray(10*1e6*data['pv']['data'].transpose([1,2,0]),dtype=np.int16),
					'eql':np.asarray(10*data['pv']['eql'].transpose([1,2,0]),dtype=np.int16),
					'lon':np.asarray(self.lons,dtype=np.double),
					'lat':np.asarray(self.lats,dtype=np.double),
				})
		data['eql'].update({
					'data':np.asarray(10*data['eql']['data'],dtype=np.int16),
					'pv':np.asarray(10*1e6*data['eql']['pv'],dtype=np.int16),
				})
		
		savemat(filename,data,oned_as='row')

