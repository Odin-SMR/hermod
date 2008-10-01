from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import UniqueObject,SimpleItemWithProperties

from permissions import BROWSE
class pictures(SimpleItemWithProperties):

        meta_type = 'Browse pictures an movies'
        #set up security
        security = ClassSecurityInfo()
        security.declareObjectProtected(BROWSE)

        security.declareProtected(BROWSE,'movie')
	def movie(self,**params):
		import os
		import tempfile
		import convert_date as c
		
		webparams = dict(**params)
		species = webparams['form.select_species']
		date_start = (int(webparams['form.select_start_year']),int(webparams['form.select_start_month']),int(webparams['form.select_start_day']))
		date_end = (int(webparams['form.select_end_year']),int(webparams['form.select_end_month']),int(webparams['form.select_end_day']))
		level = int(webparams['form.select_level'])
		set_fps = webparams['form.select_fps']
		
		if level == 475:
			level_num = 0
		elif level == 525:
			level_num = 1
		elif level == 575:
			level_num = 2
		elif level == 625:
			level_num = 3
		
		date_start_mjd = c.utc2mjd(date_start[0],date_start[1],date_start[2])
		date_end_mjd = c.utc2mjd(date_end[0],date_end[1],date_end[2])
		
		filename = '/tmp/%s.txt' % os.getpid()
		temp = open(filename, "w+b+t")
		for i in range(date_start_mjd,date_end_mjd+1,1):
			year,month,day,hour,minute,secs,ticks = c.mjd2utc(i)
			temp.write('/odin/extdata/PICTURES/' + species + '/' + str(year) + '/' + str(month) + '/' + species + '_' + str(level_num) + '_' + str(i) + '.png\n')
		temp.close()
		os.system("mencoder 'mf://@" + filename + "' -mf type=png:fps=" + set_fps + " -ovc lavc -lavcopts vcodec=wmv2 -oac copy -o /home/marjan/test/animation1.avi")
		os.remove(filename)
		
        security.declareProtected(BROWSE,'save_fig')
	def save_fig(self,**params):
		import os
		import convert_date as c
		
		webparams = dict(**params)
		species = webparams['form.select_species']
		date_start = (int(webparams['form.select_start_year']),int(webparams['form.select_start_month']),int(webparams['form.select_start_day']))
		date_end = (int(webparams['form.select_end_year']),int(webparams['form.select_end_month']),int(webparams['form.select_end_day']))
		level = int(webparams['form.select_level'])
				
		date_start_mjd = c.utc2mjd(date_start[0],date_start[1],date_start[2])
		date_end_mjd = c.utc2mjd(date_end[0],date_end[1],date_end[2])
		
		if level == 475:
			level_num = 0
		elif level == 525:
			level_num = 1
		elif level == 575:
			level_num = 2
		elif level == 625:
			level_num = 3
		
		for i in range(date_start_mjd,date_end_mjd+1,1):
			year,month,day,hour,minute,secs,ticks = c.mjd2utc(i)
			os.system('cp /odin/extdata/PICTURES/' + species + '/' + str(year) + '/' + str(month) + '/' + species + '_' + str(level_num) + '_' + str(i) + '.png' + ' ' + '/home/marjan/test/' + species + '_' + str(level) + '_' + str(year) + '%02d%02d.png' %(month,day))
			

InitializeClass(pictures)
