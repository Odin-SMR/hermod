form = context.REQUEST.form
data = context.odinsmrsite_download.searchData(**form)
state.setKwargs(form)
print form
state.setKwargs( {'portal_status_message':'form : %s' %(str(form),)} )
state.set(data=data)
return state
