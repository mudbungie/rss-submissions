import uuid
import datetime
import cgi
import subprocess
import os
import unidecode
import ftfy
import unicodedata
import rssgen
import xmlgen

PathToContent = 'content/'

class UserError(Exception):
	def __init__(self, message):
		self.message = message
	def __str__(self):
		return message

class thumbnail:
	def __init__(self, imageFile):
		metadataExtractionCommand = 'identify "' + PathToContent + imageFile + '" -verbose'
		print(metadataExtractionCommand)
		self.fileName = imageFile
		metadata = subprocess.check_output(metadataExtractionCommand, shell=True).decode('UTF=8').split(' ')
		self.type = metadata[1]
		self.resolution = metadata[2]
		print(self.resolution)
		self.width = self.resolution.split('x')[0]
		self.height = self.resolution.split('x')[1]

class video:
	def getDuration(self, durationLine):
		durationInSeconds = 0
		listIndex = 0
		durationLineSplit = durationLine.split(' ')
		for timeQuantity in durationLineSplit:
			listIndex = listIndex + 1
			if timeQuantity.endswith('h'):
				durationInSeconds = durationInSeconds + (int(timeQuantity.split('h')[0]) * 3600)
			if timeQuantity.endswith('mn'):
				durationInSeconds = durationInSeconds + (int(timeQuantity.split('mn')[0]) * 60)
			if timeQuantity.endswith('s') and not timeQuantity.endswith('ms'):
				durationInSeconds = durationInSeconds + (int(timeQuantity.split('s')[0]))
		return str(durationInSeconds)
	def __init__(self, videoFile):
		self.fileName = videoFile
		metadataExtractionCommand = 'mediainfo "' + PathToContent + self.fileName + '"'
		# takes all the metadata and gives a list of strings
		metadata = subprocess.check_output(metadataExtractionCommand, shell=True).decode('UTF=8').split('\n')
		for line in metadata:
			if line.startswith('Duration'):
				self.duration = self.getDuration(line.split(':')[1])
		self.type = ('video/mp4')

def form():
	with open('staticAssets/dsportal.html', 'r')	as html:
		yield(html.read().encode('utf-8'))

def writeItem(postStrings):
	feedURL = 'http://172.16.1.150/'
	contentURIFragment = 'content/'
	contentURL = feedURL + contentURIFragment
	
	# I'm honestly just extracting these because it makes it easier to read in the XML knot.
	title = postStrings['title']
	guid = postStrings['guid']
	description = postStrings['description']
	keywords = postStrings['keywords']
	pubDate = postStrings['pubDate']
	postThumbnail = postStrings['uploadThumbnail']
	postVideo = postStrings['uploadVideo']
	postThumbnailHeight = postStrings['uploadThumbnailHeight']
	postThumbnailWidth = postStrings['uploadThumbnailWidth']
	postVideoDuration = postStrings['uploadVideoDuration']

	# initialize the tags
	item = xmlgen.XMLEnclosedTag('item')
	itemGuid = xmlgen.XMLEnclosedTag('guid')
	itemGuid.addContent(guid)
	itemTitle = xmlgen.XMLEnclosedTag('title')
	itemTitle.addContent(title)
	itemDescription = xmlgen.XMLEnclosedTag('description')
	itemDescription.addContent(description)
	itemAuthor = xmlgen.XMLEnclosedTag('author')
	itemAuthor.addContent('DeskSite')
	itemMediaContent = xmlgen.XMLEnclosedTag('media:content')
	itemMediaContent.addAttrib('duration', postVideoDuration)
	itemMediaContent.addAttrib('type', 'video/mp4')
	itemMediaContent.addAttrib('url', contentURL + postVideo)
	itemMediaThumbnail = xmlgen.XMLTag('media:thumbnail')
	itemMediaThumbnail.addAttrib('url', contentURL + postThumbnail)
	itemMediaThumbnail.addAttrib('type', 'image/jpeg')
	itemMediaThumbnail.addAttrib('height', postThumbnailHeight)
	itemMediaThumbnail.addAttrib('width', postThumbnailWidth)
	itemMediaTitle = xmlgen.XMLEnclosedTag('media:title')
	itemMediaTitle.addContent(title)
	itemMediaCopyright = xmlgen.XMLEnclosedTag('media:copyright')
	itemMediaCopyright.addContent('DeskSite')
	itemPubDate = xmlgen.XMLEnclosedTag('pubdate')
	itemPubDate.addContent(pubDate)
	itemMediaKeywords = xmlgen.XMLEnclosedTag('media:keywords')
	itemMediaKeywords.addContent(keywords)
	print(itemMediaThumbnail.values['url'])

	# wrap up the XML
	item.addChildTag(itemGuid)
	item.addChildTag(itemTitle)
	item.addChildTag(itemDescription)
	item.addChildTag(itemAuthor)
	item.addChildTag(itemMediaContent)
	item.addChildTag(itemPubDate)
	item.addChildTag(itemMediaKeywords)

	itemMediaContent.addChildTag(itemMediaThumbnail)
	itemMediaContent.addChildTag(itemMediaTitle)
	itemMediaContent.addChildTag(itemMediaCopyright)

	completedItem = item.publish()
	# return it as a big string
	with open('preview/' + pubDate + postVideo + '.xml', 'w') as xmlFile:
		xmlFile.write(completedItem)
	return completedItem
	
def parseHTTPPost(HTTPPost):
	# takes the FieldStorage object, does verification, and returns a dict of strings
	# for the simple values, these are unmodified from the original contents of HTTPPost,
	# with the exception of character substution for dangerous or unsupported characters
	# For files, this saves them to the CDN directory under unique names, and returns 
	# those file names. I'm also generating the uuid/pubdate in here. That is partly because
	# I might want to make uuids/pubdates submittable in the future, and partly because it
	# just feels neater to do everything in here.
	postParsed = {}
	postParsed['pubDate'] = datetime.datetime.now().isoformat().split('.')[0]
	postParsed['guid'] = str(uuid.uuid4().int)

	# do all the things necessary to make sure that we aren't proceeding with strings
	# that we can safely use
	def verifyString(HTTPPost, fieldName):
		field = HTTPPost[fieldName].value

#		for character in field:
#			if str(hex(ord(character))) == '0xfffd':
#				print('Stop using Word.')
#				raise UserError('Stop using Word')

		# cut out characters poisonous to XML
		field = field.replace('&', '&amp;')
		field = field.replace('\"', '&quot;')
		field = field.replace('\'', '&apos;')
		field = field.replace('<', '&lt;')
		field = field.replace('>', '&gt;')
		
		# assign limitations specific to the different strings
		if fieldName == 'title':
			maxLength = 60
			minLength = 1
		elif fieldName == 'description':
			maxLength = 350
			minLength = 1
		elif fieldName == 'keywords':
			maxLength = 250
			minLength = 1
			delimitingChar = ','
			numberOfDelimiters = 2
		else:
			raise UserError(fieldName)
		# check those limitations
		if len(field) > maxLength:
			raise UserError(fieldName + ' too long')
		elif len(field) < minLength:
			raise UserError(fieldName + ' too short')
		try:
			if field.count(delimitingChar) > numberOfDelimiters:
				raise UserError(fieldName + ' has the wrong number of delimiters')
		except NameError:
			# because only keywords actually have this field
			pass
		return field

	postParsed['title'] = verifyString(HTTPPost, 'title')
	postParsed['description'] = verifyString(HTTPPost, 'description')
	postParsed['keywords'] = verifyString(HTTPPost, 'keywords')

	# takes a file and its name, saves it, returns the filename
	def saveUpload(upload, postDict):
		uploadFileName = postDict['pubDate'].replace(':', '') + upload.filename.replace(':', '_').replace(' ', '')
		with open(PathToContent + uploadFileName, 'wb') as uploadFile:
			uploadFile.write(upload.value)
		return uploadFileName

	postParsed['uploadThumbnail'] = saveUpload(HTTPPost['uploadThumbnail'], postParsed)
	postThumbnail = thumbnail(postParsed['uploadThumbnail'])
	postParsed['uploadThumbnailHeight'] = postThumbnail.height
	postParsed['uploadThumbnailWidth'] = postThumbnail.width

	postParsed['uploadVideo'] = saveUpload(HTTPPost['uploadVideo'], postParsed)
	postVideo = video(postParsed['uploadVideo'])
	postParsed['uploadVideoDuration'] = postVideo.duration

	return postParsed

def preview(HTTPPost):
	# clear out any old previews
	for listing in os.listdir(path = 'preview/'):
		os.remove('preview/' + listing)
	
	# turn the post into a bunch of strings
	try:
		postStrings = parseHTTPPost(HTTPPost)
	except UserError:
		return('Stop using Word.'.encode('utf-8'))
	# write it out in XML
	postXML = writeItem(postStrings)

	# wrap it up with a preview RSS page so that browsers know how to render it
	demoRSS = rssgen.demo(postXML)
	
	# give it to the browser
	return demoRSS

def post():
	successfulPost = False
	for listing in os.listdir(path = 'preview/'):
		os.rename('preview/' + listing, 'items/' + listing)
	return ('Most recently previewed page is now live.'.encode('utf-8'))

def deletionForm():
	with open('staticAssets/deletion.html', 'r') as html:
		return html.read().encode('utf-8')

def deletePostByGUID(HTTPPost):
	pathToXML = 'items/'

	# take the GUID that it was passed
	guid = HTTPost['guid'].value

	# find any files with that GUID and delete them
	for fileName in os.listdir(pathToXML):
		print(fileName)
		deleteIt = False
		with open(pathToXML + fileName, 'r') as xmlFile:
			for line in xmlFile.read().splitlines():
				print(line)
				if line.startswith('<guid>'):
					print(line)
					guid = line.split('>')[1].split('<')[0]
					print(guid)
					if guid == targetGuid:
						print("match!")
						targetFile = fileName
						deleteIt = True
		if deleteIt:
			os.remove(pathToXML + targetFile)

def fileRequest(requestPath, startResponse):
	def returnFile(location, MIMEString, encoding = None, binary = False):
		if binary:	
			readAs = 'rb'
		else:
			readAs = 'r'
		with open(location, readAs) as requestedFile:
			startResponse('200 OK', [('Content-Type', MIMEString)])
			if encoding is not None:
				return(requestedFile.read().encode(encoding))
			else:
				return(requestedFile.read())

	if requestPath.endswith('.mp4'):
		return(returnFile('content/' + requestPath.split('/')[-1], 'video/mp4;', binary = True))
	elif requestPath.endswith('.jpg'):
		return(returnFile('content/' + requestPath.split('/')[-1], 'image/jpeg;', binary = True))
	elif requestPath.endswith('.html'):
		return(returnFile('staticAssets/' + requestPath.split('/')[-1], 'text/html; charset = utf-8', encoding = 'utf-8'))
	elif requestPath.endswith('.js'):
		return(returnFile('staticAssets/' + requestPath.split('/')[-1], 'text/javascript; charset = utf-8', encoding = 'utf-8'))
	elif requestPath.endswith('.css'):
		return(returnFile('staticAssets/' + requestPath.split('/')[-1], 'text/css; charset = utf-8', encoding = 'utf-8'))
