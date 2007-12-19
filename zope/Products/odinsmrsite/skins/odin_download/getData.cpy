form = context.REQUEST.form
data = context.data_download.searchData(**form)
state.setKwargs(form)
state.setKwargs( {'portal_status_message':'form : %s' %(str(form),)} )
state.set(data=data)
return state
