form = context.REQUEST.form
data = context.odin_pictures.save_fig(**form)
state.setKwargs(form)
state.setKwargs( {'portal_status_message':'form : %s' %(str(form),)} )
state.set(data=data)
return state
