
form = context.REQUEST.form
context.data_download.downloadData(**form)
#state.setKwargs(form)
state.setKwargs( {'portal_status_message':'uploaded'} )
return state
