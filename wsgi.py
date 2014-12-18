import urllib.parse
import dsportal
import cgitb
import cgi
import rssgen

cgitb.enable()

def application(env, startResponse):
	method = env['REQUEST_METHOD']
	try:
		contentLength = int(env['CONTENT_LENGTH'])
		postEnv = env.copy()
		postEnv['QUERY STRING'] = ''
		HTTPPost = cgi.FieldStorage(fp = env['wsgi.input'], environ = postEnv, keep_blank_values = True)
	except ValueError:
		pass
	

	path = env['PATH_INFO']

	if method == 'GET':
		if path == '/':
			startResponse('200 OK', [('Content-Type', 'application/xml; charset = utf-8')])
			return(rssgen.feed())
		if path == '/form':
			startResponse('200 OK', [('Content-Type', 'text/html; charset = utf-8')])
			return(dsportal.form())
		elif path == '/deletion':
			startResponse('200 OK', [('Content-Type', 'text/html; charset = utf-8')])
			return(dsportal.deletionForm())
		else:
			return(dsportal.fileRequest(path, startResponse))
	elif method == 'POST':
		if path == '/video-stage':
			startResponse('200 OK', [('Content-Type', 'application/xml; charset = utf-8')])
			return(dsportal.preview(HTTPPost))
		elif path == '/video-commit':
			startResponse('200 OK', [('Content-Type', 'text/html; charset = utf-8')])
			return(dsportal.post())
		elif path == '/video-delete':
			startResponse('200 OK', [('Content-Type', 'application/xml; charset = utf-8')])
			return(dsportal.deletePostByGUID(HTTPPost))
	else:
		startResponse('200 OK', [('Content-Type', 'text/html; charset = utf-8')])
		return('Malformed request').encode('utf-8')
