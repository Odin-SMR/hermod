form = context.REQUEST.form
#insert checks here
state.setKwargs(form)

# Date earlier than the first date with values
if (form['form.select_start_year_p']=="2001") & (int(form['form.select_start_month_p'])<10):
    state.setError('select_start_year_p','Not a valid start date',new_status='failure')
    state.set(portal_status_message=('Please correct the errors.'))
    
if (form['form.select_end_year_p']=="2001") & (int(form['form.select_end_month_p'])<10):
    state.setError('select_end_year_p','Not a valid end date',new_status='failure')
    state.set(portal_status_message=('Please correct the errors.'))
 
# End date earlier than start date   
if int(form['form.select_start_year_p'])>int(form['form.select_end_year_p']):
    state.setError('select_end_year_p','The time period ends before it starts',new_status='failure')
    state.set(portal_status_message=('Please correct the errors.')) 
     
if (form['form.select_start_year_p']==form['form.select_end_year_p']) & (int(form['form.select_end_month_p'])<int(form['form.select_start_month_p'])):
    state.setError('select_end_year_p','The time period ends before it starts',new_status='failure')
    state.set(portal_status_message=('Please correct the errors.'))
    
if (form['form.select_start_year_p']==form['form.select_end_year_p']) & (form['form.select_start_month_p']==form['form.select_end_month_p']) & (int(form['form.select_end_day_p'])<int(form['form.select_start_day_p'])):
    state.setError('select_end_year_p','The time period ends before it starts',new_status='failure')
    state.set(portal_status_message=('Please correct the errors.'))

# Months with less days than 31
month = [4,6,9,11]
for i in month:
	if ((form['form.select_start_month_p']==str(i)) & (form['form.select_start_day_p']=="31")):
		state.setError('select_start_year_p','Not a valid date',new_status='failure')
		state.set(portal_status_message=('Please correct the errors.'))
	if (form['form.select_end_month_p']==str(i)) & (form['form.select_end_day_p']=="31"):
		state.setError('select_end_year_p','Not a valid date',new_status='failure')
		state.set(portal_status_message=('Please correct the errors.'))
		
# February and leap years

leap_year_start = 'yes'
leap_year_end = 'yes'

if int(form['form.select_start_year_p'])%4!=0:             
	leap_year_start = 'no'             
if int(form['form.select_start_year_p'])%100==0:           
	leap_year_start = 'no'
if int(form['form.select_start_year_p'])%400==0:	      
	leap_year_start = 'yes'

if int(form['form.select_end_year_p'])%4!=0:              
	leap_year_end = 'no'             
if int(form['form.select_end_year_p'])%100==0:           
	leap_year_end = 'no'
if int(form['form.select_end_year_p'])%400==0:	       
	leap_year_end = 'yes'	
	
if (form['form.select_start_month_p']=="2") & (int(form['form.select_start_day_p'])>29) & (leap_year_start == 'yes'):
	state.setError('select_start_year_p','Not a valid date 1',new_status='failure')
	state.set(portal_status_message=('Please correct the errors.'))
elif (form['form.select_start_month_p']=="2") & (int(form['form.select_start_day_p'])>28) & (leap_year_start == 'no'):
	state.setError('select_start_year_p','Not a valid date 2',new_status='failure')
	state.set(portal_status_message=('Please correct the errors.'))

if (form['form.select_end_month_p']=="2") & (int(form['form.select_end_day_p'])>29) & (leap_year_end == 'yes'):
	state.setError('select_end_year_p','Not a valid date',new_status='failure')
	state.set(portal_status_message=('Please correct the errors.'))
elif (form['form.select_end_month_p']=="2") & (int(form['form.select_end_day_p'])>28) & (leap_year_end == 'no'):
	state.setError('select_end_year_p','Not a valid date',new_status='failure')
	state.set(portal_status_message=('Please correct the errors.'))	

return state
