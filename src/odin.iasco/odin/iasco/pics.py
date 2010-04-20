#!/usr/bin/python
# coding: UTF-8

from plot import globalPlot,polarPlot
from convert_date import utc2mjd,mjd2utc
import os.path
from odin.config.environment import *
#from odinsite.level3.register import registerObject

#for mjd in range(52375,52376):#,52306):
#    for species in ['O3_501','O3_544','H2O','HNO3','N2O']:
#        for level in potLevel[species]:
#            year,month,day,hour,minute,sec,tic=mjd2utc(mjd)
#            inst.createLevel3Object(u'odin_wp',u'marjan',str(year),str(month),str(day),species,level)
 
def makePictures(date,fqid,zope): 
    """
    Generation of pictures for one date and fqid at the time
    """
    date_mjd=utc2mjd(date.year,date.month,date.day)
    
    ### Define species          
    if fqid==29:
        species = ['O3_501','N2O']       
    if fqid==3:
        species = ['O3_544','HNO3','H2O']      
    
    ### The number of potential temperature levels for the various species        
    for spec in species:
        if spec == 'O3_501' or spec=='O3_544' or spec=='N2O':
            levels = [0,1,2,3]
        elif spec == 'HNO3' or spec=='H2O':
            levels = [0,1,2,3,4,5]

        ### Generation of global plots
        for level in levels: 
            globalPlot(date_mjd,level,spec)
            #inst=registerObject('parts/instance/etc/zope.conf')
            year,month,day,hour,minute,sec,tic=mjd2utc(date_mjd)
            #inst.createLevel3Object(u'odin_wp',u'marjan',str(year),str(month),str(day),species,str(level))
            zope.stdin.write("%s,%s,%s,%s,%s\n"%(year,month,day,spec,level))

        file_501=config.get('GEM','LEVEL3_DIR') + 'DATA/O3_501/' + str(date.year) + '/' + str(date.month) + '/' + 'O3_501_' + str(date_mjd) + '_00.mat'
        file_544=config.get('GEM','LEVEL3_DIR') + 'DATA/O3_544/' + str(date.year) + '/' + str(date.month) + '/' + 'O3_544_' + str(date_mjd) + '_00.mat' 
        if os.path.exists(file_501) and os.path.exists(file_544):
            ### Generation of polar plots. Needs data from all the species, hence the if-statement. 
            for level in range(0,2):        
                polarPlot(date_mjd,level)
