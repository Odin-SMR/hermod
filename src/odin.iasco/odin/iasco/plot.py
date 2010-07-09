#!/usr/bin/python
# coding: UTF-8

"""
plot.py plots measured and simulated data from the ODIN satellite and the simulation program IASCO. The plots are projected eather on a world map (Miller projection) och on the north and south pole. For more information on how to use these different applications, please see the documentation for globalPlot and polarPlot respectivly.
"""

import convert_date as c
import color_axis as col
from scipy import io as sio
import matplotlib as matplotlib
matplotlib.use('Agg')
import os
import numpy as n
from mpl_toolkits.basemap import Basemap,shiftgrid
from pylab import *
import gc
from datetime import date as dt
from odin.config.environment import *

def globalPlot(date_mjd,level,species):
    """
    Function for a global plot. The figure shows a plot over the world map for the chosen species (O3 501.8 GHz, O3 544.6 GHz, H2O, N2O, HNO3). Inputs are the date defined in Modified Julian Date, the potential temperature level of interest (see table below) and the species of interest (date and level (0 to 5) should be defined as integers while the species is defined as a string).

              0     1     2     3     4     5
    O3_501 | 475 | 525 | 575 | 625 | --- | ---
    O3_544 | 475 | 525 | 575 | 625 | --- | ---
       N2O | 475 | 525 | 575 | 625 | --- | ---
       H2O | 400 | 425 | 450 | 475 | 500 | 525
      HNO3 | 475 | 525 | 575 | 625 | 675 | 725
  
    Example: globalPlot(54745,2,'O3_501') - Will plot a global projection for 2008-10-06 for O3 (510.8 GHz) at the potential temperature level 575 K.
    """
    year,month,day,hour,minute,secs,tics = c.mjd2utc(date_mjd)
    load_path = config().get('GEM','LEVEL3_DIR') + 'DATA/'
    data = sio.loadmat(load_path + species + '/' + str(year) + '/' + str(month) + '/' + species + '_' + str(date_mjd) + '_00.mat')
    data=double(data['TracerField_u16'])*data['K_TracerField']
    m = Basemap(projection='mill') # Makes a Miller projection of the world map

    # Defines latitudes and longitudes and makes a transformation of the data coordinates to fit the coordinates of the map (basemap)
    lats = n.arange(-88.875,88.875+2.25,2.25)
    lons = n.arange(-178.875,178.875+2.25,2.25)
    nx = 320
    ny = 160
    specdat = m.transform_scalar(data[:,:,level], lons, lats, nx, ny)
	
    clf() # Makes the figure
    fig = figure(figsize=(8,6))
    caxis, step = col.c_axis(level,species)
    
    im = m.imshow(specdat*1e6, interpolation='bilinear', vmin=caxis[0], vmax=caxis[1]+0.0000001*step,origin='upper')
    colorbar(im,orientation='vertical',shrink=0.76,ticks=n.arange(caxis[0],caxis[1]+step,step))
    m.drawcoastlines()
    m.drawmeridians(range(-135,136,45),labels=[1,0,0,1])
    m.drawparallels([-75,-45,0,45,75],labels=[1,0,0,1])
    
    titles = ['O3 (501.8 GHz)','O3 (544.6 GHz)']
    
    # Makes title and figure texts
    if (species == 'N2O'):
        if level == 0:
            title(species + '\nDate: %d-%02d-%02d Level: 475K' %(year,month,day) )
        elif level == 1:
            title(species + '\nDate: %d-%02d-%02d Level: 525K' %(year,month,day) )
        elif level == 2:
            title(species + '\nDate: %d-%02d-%02d Level: 575K' %(year,month,day) )  
        elif level == 3:
            title(species + '\nDate: %d-%02d-%02d Level: 625K' %(year,month,day) )
    if (species == 'O3_501'):
        if level == 0:
            title(titles[0] + '\nDate: %d-%02d-%02d Level: 475K' %(year,month,day) )
        elif level == 1:
            title(titles[0] + '\nDate: %d-%02d-%02d Level: 525K' %(year,month,day) )
        elif level == 2:
            title(titles[0] + '\nDate: %d-%02d-%02d Level: 575K' %(year,month,day) )  
        elif level == 3:
            title(titles[0] + '\nDate: %d-%02d-%02d Level: 625K' %(year,month,day) )		
    if (species == 'O3_544'):
        if level == 0:
            title(titles[1] + '\nDate: %d-%02d-%02d Level: 475K' %(year,month,day) )
        elif level == 1:
            title(titles[1] + '\nDate: %d-%02d-%02d Level: 525K' %(year,month,day) )
        elif level == 2:
            title(titles[1] + '\nDate: %d-%02d-%02d Level: 575K' %(year,month,day) )  
        elif level == 3:
            title(titles[1] + '\nDate: %d-%02d-%02d Level: 625K' %(year,month,day) )		
    elif species == 'H2O':
        if level == 0:
            title(species + '\nDate: %d-%02d-%02d Level: 400K' %(year,month,day) )
        elif level == 1:
            title(species + '\nDate: %d-%02d-%02d Level: 425K' %(year,month,day) )
        elif level == 2:
            title(species + '\nDate: %d-%02d-%02d Level: 450K' %(year,month,day) )  
        elif level == 3:
            title(species + '\nDate: %d-%02d-%02d Level: 475K' %(year,month,day) )
        elif level == 4:
            title(species + '\nDate: %d-%02d-%02d Level: 500K' %(year,month,day) )  
        elif level == 5:
            title(species + '\nDate: %d-%02d-%02d Level: 525K' %(year,month,day) )
    elif species == 'HNO3':
        if level == 0:
            title(species + '\nDate: %d-%02d-%02d Level: 475K' %(year,month,day) )
        elif level == 1:
            title(species + '\nDate: %d-%02d-%02d Level: 525K' %(year,month,day) )
        elif level == 2:
            title(species + '\nDate: %d-%02d-%02d Level: 575K' %(year,month,day) )  
        elif level == 3:
            title(species + '\nDate: %d-%02d-%02d Level: 625K' %(year,month,day) )
        elif level == 4:
            title(species + '\nDate: %d-%02d-%02d Level: 675K' %(year,month,day) )  
        elif level == 5:
            title(species + '\nDate: %d-%02d-%02d Level: 725K' %(year,month,day) )
		
    c_str='Copyright (c) ' + str(dt.today().year) + ' Chalmers tekniska högskola AB'
    figtext(0.26,0.14, c_str.decode('UTF-8'),fontsize=8)
    figtext(0.325,0.115,'Marcus Jansson & Erik Zakrisson',fontsize=8)
    if species == 'HNO3':
       	figtext(0.885,0.465,'[ppm]',fontsize=12,rotation='vertical')
    else:
        figtext(0.865,0.465,'[ppm]',fontsize=12,rotation='vertical')
	
    # Save the images divided into folders according to species, year and month
    save_path_main=(config().get('GEM','LEVEL3_DIR') + 'PICTURES')

    if not os.path.isdir(save_path_main + '/'):
        os.mkdir(save_path_main + '/')
    if not os.path.isdir(save_path_main + '/' + species + '/'):
        os.mkdir(save_path_main + '/' + species + '/')
    if not os.path.isdir(save_path_main + '/' + species + '/' + str(year) + '/'):
        os.mkdir(save_path_main + '/' + species + '/' + str(year) + '/')
    if not os.path.isdir(save_path_main + '/' + species + '/' + str(year) + '/' + str(month) + '/'):
        os.mkdir(save_path_main + '/' + species + '/' + str(year) + '/' + str(month) + '/')
		
    savefig(os.path.join(save_path_main + '/' + species + '/' + str(year) + '/' + str(month) + '/', species + '_' + str(level) + '_' + str(date_mjd) + '.png'))
    gc.collect()

def polarPlot(date_mjd,level):
    """
    Function for a plot over the polar regions. The figure shows subplots for all species (O3 (501.8 GHz), H2O, N2O, HNO3) and for the south pole and the north pole respectively. Inputs are the date defined in Modified Julian Date and the potential temperature level of interest (0 => 475K, 1 => 525K) these are the levels that are mutual between the four species.

    Example: polarPlot(54745,0) - Will plot a polar projection for 2008-10-06 at the potential temperature level 475 K.
    """
    import matplotlib.colors as colors

    species=['O3_501','H2O','N2O','HNO3']
    titles=['O3 (501.8 GHz)','H2O','N2O','HNO3']
    # The temperatur levels 475K and 525K corresponds to level 3 and 5 in the data matrix for H2O (0 and 1 for all the other)
    if level == 0: 
        level_H2O = 3
    elif level == 1:
        level_H2O = 5
    else:
        level_H2O = level
    levels = [level,level_H2O,level,level]
		
    year,month,day,hour,minute,secs,tics = c.mjd2utc(date_mjd)
    # Makes the figure with head title and figure texts
    clf()
    fig = figure(figsize=(12,6)) 
    axis('off')
	
    if level == 0:
        figtext(0.375,0.88,'Date: %d-%02d-%02d Level: 475K\n' %(year,month,day), fontsize=14 )
    elif level == 1:
        figtext(0.365,0.91,'Date: %d-%02d-%02d Level: 525K\n' %(year,month,day), fontsize=14 )
    else:
        figtext(0.365,0.91,'Date: %d-%02d-%02d Level: ...\n' %(year,month,day), fontsize=14 )

		
    c_str='Copyright (c) ' + str(dt.today().year) + ' Chalmers tekniska högskola AB'
    figtext(0.375,0.1, c_str.decode('UTF-8'),fontsize=8)
    figtext(0.42,0.076,'Marcus Jansson & Erik Zakrisson',fontsize=8)
    figtext(0.038,0.713,'North Pole', fontsize=12)
    figtext(0.038,0.275,'South Pole', fontsize=12)
    figtext(0.92,0.484,'[ppm]',fontsize=12,rotation='horizontal')
    load_path = config().get('GEM','LEVEL3_DIR') + 'DATA/'
    for i in range(0,len(species)): # Makes subplots for each species
	
        data = sio.loadmat(load_path + species[i] + '/' + str(year) + '/' + str(month) + '/' + species[i] + '_' + str(date_mjd) + '_00.mat')
        data=double(data['TracerField_u16'])*data['K_TracerField']
        mN = Basemap(lon_0=0,resolution='c',area_thresh=10000.,boundinglat=20., projection='npstere') # North pole projection
        mS = Basemap(lon_0=0,resolution='c',area_thresh=10000.,boundinglat=-20., projection='spstere') # South pole projection
        # Define Latitudes and longitudes
        lats = n.arange(-88.875,88.875+2.25,2.25)
        lats = lats*90/lats[-1]
        lons = n.arange(-180,180+2.25,2.25)
        N_lat = len(lats)
        N_lon = len(lons)
	
        if species[i] == 'H2O' or species[i] == 'HNO3':
            no_of_levels = 6
        else:
            no_of_levels = 4
        specdata=zeros((80,161,no_of_levels))
        for k in range(0,no_of_levels): # Add an extra column at the poles
            for l in range(0,80):
                for o in range(0,161):
                    if o==160:
                        specdata[l,o,k]=data[l,o-1,k]
                    else:
                        specdata[l,o,k]=data[l,o,k]
        # Flip the matrix so the values is correct (upper left corner (0,0) in the data matrix represent the lower left corner of the map.)
        data=zeros((80,161,no_of_levels))
        for j in range(0,no_of_levels): 
            data[:,:,j]=flipud(specdata[:,:,j])
		
        # Makes a transformation of the data coordinates to fit the coordinates of the map (basemap)
        dxN = 2.*pi*mN.rmajor/len(lons)
        nxN = int((mN.xmax-mN.xmin)/dxN)+1
        nyN = int((mN.ymax-mN.ymin)/dxN)+1
        dxS = 2.*pi*mS.rmajor/len(lons)
        nxS = int((mS.xmax-mS.xmin)/dxS)+1
        nyS = int((mS.ymax-mS.ymin)/dxS)+1
        specdataN = mN.transform_scalar(data[:,:,levels[i]], lons, lats, nxN, nyN, masked=True)
        specdataS = mS.transform_scalar(data[:,:,levels[i]], lons, lats, nxS, nyS, masked=True)
		
        # Makes the images, north- and south pole
        caxis,step = col.c_axis(levels[i],species[i])
        axN=fig.add_subplot(2,4,i+1)
        imN = mN.imshow(specdataN*1e6, norm=colors.normalize(clip=False), interpolation='bicubic', vmin=caxis[0], vmax=caxis[1])
        colorbar(shrink=0.75)
        mN.drawcoastlines()
        mN.drawmeridians(n.arange(0.,360.,60.))
        mN.drawparallels(n.arange(-80.,90,20.))
        title(titles[i], fontsize=12)
		
        axS = fig.add_subplot(2,4,i+5)
        imS = mS.imshow(specdataS*1e6, norm=colors.normalize(clip=False), interpolation='bicubic', vmin=caxis[0], vmax=caxis[1])
        colorbar(shrink=0.75)
        mS.drawcoastlines()
        mS.drawmeridians(n.arange(0.,360.,60.))
        mS.drawparallels(n.arange(-80.,90,20.))

    # Save the images divided into folders according to year and month
    save_path_main=(config().get('GEM','LEVEL3_DIR') + 'PICTURES/')
    if not os.path.isdir(save_path_main):
        os.mkdir(save_path_main)
    if not os.path.isdir(save_path_main + 'Polar/'):
        os.mkdir(save_path_main + 'Polar/')
    if not os.path.isdir(save_path_main  + 'Polar/' + str(year) + '/'):
            os.mkdir(save_path_main + 'Polar/' + str(year) + '/')
    if not os.path.isdir(save_path_main + 'Polar/'  + str(year) + '/' + str(month) + '/'):
            os.mkdir(save_path_main + 'Polar/' + str(year) + '/' + str(month) + '/')

    savefig(os.path.join(save_path_main + 'Polar/' + str(year) + '/' + str(month) + '/', 'Polar_' + str(level) + '_' + str(date_mjd) + '.png'))
    gc.collect()
