form = context.REQUEST.form
data = context.data_download.searchL2(**form)
context.data_download.status(form)
state.setKwargs( {'portal_status_message':'form : %s' %(str(form),)} )
state.setKwargs(form)
state.set(data=data)
return state
