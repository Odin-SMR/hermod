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
                from subprocess import Popen,PIPE
                from tempfile import NamedTemporaryFile
		
                ## grabbing Response-object and set useful headers
                response = self.REQUEST.RESPONSE
                response.setHeader('Pragma','no-cache')
                response.setHeader('content-coding','video/x-msvideo')
		
		webparams = dict(**params)

                species = webparams['form.select_species_m']
		date_start = (int(webparams['form.select_start_year_m']),int(webparams['form.select_start_month_m']),int(webparams['form.select_start_day_m']))
		date_end = (int(webparams['form.select_end_year_m']),int(webparams['form.select_end_month_m']),int(webparams['form.select_end_day_m']))
		level = int(webparams['form.select_level_m'])
		set_fps = int(webparams['form.select_fps'])
		
		
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
		
                #temporary files in /tmp dir
		temp = NamedTemporaryFile()
                mov = NamedTemporaryFile()
                
		for i in range(date_start_mjd,date_end_mjd+1,1):
			year,month,day,hour,minute,secs,ticks = c.mjd2utc(i)
                        #creating filelist in a tempfile
			temp.write('/odin/extdata/PICTURES/' + species + '/' + str(year) + '/' + str(month) + '/' + species + '_' + str(level_num) + '_' + str(i) + '.png\n')

                #start over at top of file
                temp.seek(0)
		os.system("mencoder mf://@%s -mf type=png:fps=%i -ovc lavc -lavcopts vcodec=wmv2 -oac copy -o %s" %(temp.name,set_fps,mov.name))
                #reset filepointer
                mov.seek(0)
                #stream movie contents to response-object
                while True:
                    data = mov.read(1024)
                    if data=='':
                        break
                    else:
                        response.write(data)
		
        security.declareProtected(BROWSE,'save_fig')
	def save_fig(self,**params):
		import os
		import convert_date as c
                from subprocess import Popen,PIPE
                from os.path import join
                #setup response-object
                response = self.REQUEST.RESPONSE
                response.setHeader('Pragma','no-cache')
                response.setHeader('content-coding','gzip')
		
		webparams = dict(**params)
		species = webparams['form.select_species_p']
		date_start = (int(webparams['form.select_start_year_p']),int(webparams['form.select_start_month_p']),int(webparams['form.select_start_day_p']))
		date_end = (int(webparams['form.select_end_year_p']),int(webparams['form.select_end_month_p']),int(webparams['form.select_end_day_p']))
		level = int(webparams['form.select_level_p'])
				
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

                #generate a list of all file matching the search criteria
		filelist = []
                base = '/odin/extdata/PICTURES/'
		for i in range(date_start_mjd,date_end_mjd+1,1):
			year,month,day,hour,minute,secs,ticks = c.mjd2utc(i)
                        filelist.append(join(species,str(year),'%i'%month,'%s_%i_%s.png'%(species,level_num,i)))
			#os.system('cp /odin/extdata/PICTURES/' + species + '/' + str(year) + '/' + str(month) + '/' + species + '_' + str(level_num) + '_' + str(i) + '.png' + ' ' + '/tmp/' + species + '_' + str(level) + '_' + str(year) + '%02d%02d.png' %(month,day))

                #create a pipe: " tar -c file1 file2 ... | gzip --fast > response object"
		tarball = Popen(['tar','-c']+filelist,stdout=PIPE,cwd=base)
                gzip = Popen(['gzip','--fast'],stdin=tarball.stdout,stdout=PIPE)
                while True:
                    data = gzip.stdout.read(1024)
                    if data == "":
                        break
                    else:
                        response.write(data)
                tarball.stdout.close()
                gzip.stdout.close()

InitializeClass(pictures)
