# XML generator

class XMLTag:
	def __init__(self, tag):
		self.tag = tag
		self.attribs = []
		self.values = {}
	def addAttrib(self, attrib, value=None):
		self.attribs.append(attrib)
		if value:
			self.values[attrib] = value
	def publish(self):
		tagString = '<' + self.tag
		for attrib in self.attribs:
			tagString = tagString + ' ' + attrib
			try:
				tagString = tagString + '=' + '"' + self.values[attrib] + '"'
			except KeyError:
				raise
		tagString = tagString + '/>'
		return tagString

class XMLEnclosedTag(XMLTag):
	def __init__(self, tag):
		self.tag = tag
		self.childTags = []
		self.attribs = []
		self.values = {}
		self.content = ''
	def addChildTag(self, child):
		self.childTags.append(child)
	def addContent(self, content):
		self.content = self.content + content
	def publish(self):
		tagString = '<' + self.tag
		for attrib in self.attribs:
			tagString = tagString + ' ' + attrib
			try:
				tagString = tagString + '=' + '"' + self.values[attrib] + '"'
			except KeyError:
				raise
		tagString = tagString + '>'
		for child in self.childTags:
			self.content = self.content + '\n' + child.publish()
		tagString = tagString + self.content
		tagString = tagString + '</' + self.tag + '>'
		return tagString

