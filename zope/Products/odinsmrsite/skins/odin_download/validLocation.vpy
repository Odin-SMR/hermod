form = context.REQUEST.form
#insert checks here
state.setKwargs(form)
if form['form.lon']=="":
    state.setError('lon','Not a valid longitude',new_status='failure')
    state.set(portal_status_message=('Please correct the errors.'))
return state
