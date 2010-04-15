#!/usr/bin/python

'''
Determines the color axes for each level and species so the scale will be the same and not vary between each image, This is made so the comparison will be easier. This function is used in plot.py.

Written by Erik Zakrisson 2008-10-03
'''

def c_axis(level,species):	
	if level == 0:
		if species == 'O3_501':
			caxis = (0,4)
		elif species == 'O3_544':
			caxis = (0.5,4)
		elif species == 'N2O':
			caxis = (0,0.35)
		elif species == 'H2O':
			caxis = (1,5.5) 
		elif species == 'HNO3':
			caxis = (0,0.016)
	elif level == 1:
		if species == 'O3_501':
			caxis = (1,5)
		elif species == 'O3_544':
			caxis = (1,4.5) 
		elif species == 'N2O':
			caxis = (0,0.35) 
		elif species == 'H2O':
			caxis = (1.5,5.5)
		elif species == 'HNO3':
			caxis = (0,0.018)
	elif level == 2:
		if species == 'O3_501':
			caxis = (1.5,6)
		elif species == 'O3_544':
			caxis = (1,5) 
		elif species == 'N2O':
			caxis = (0,0.35)
		elif species == 'H2O':
			caxis = (1.5,6)
		elif species == 'HNO3':
			caxis = (0,0.016)	
	elif level == 3:
		if species == 'O3_501':
			caxis = (1,7) 
		elif species == 'O3_544':
			caxis = (1,7) 
		elif species == 'N2O':
			caxis = (0,0.35)
		elif species == 'H2O':
			caxis = (1.5,6)
		elif species == 'HNO3':
			caxis = (0,0.014)
	elif level == 4:
		if species == 'H2O':
			caxis = (2,6)
		elif species == 'HNO3':
			caxis = (0,0.013)
		else:
			print 'Wrong level for', species
	elif level == 5:
		if species == 'H2O':
			caxis = (1.5,6)
		elif species == 'HNO3':
			caxis = (0,0.010)
		else:
			print 'Wrong level for', species


	if species == 'N2O':
		step = 0.05
	elif species == 'HNO3':
		step = 0.002
	elif (species == 'H2O') | (species == 'O3_501') | (species == 'O3_544'):
		step = 0.5
	
	return caxis, step
