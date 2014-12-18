import xmlgen
import os

def feed():
	RSSVersion = '2.0'
	XSI = 'http://www.w3.org/2001/XMLSchema-instance'
	XMLNS = 'http://search.yahoo.com/mrss/'
	title = 'DeskSite Video RSS'
	link = 'http://172.16.1.150/'
	description = 'Video provision for MSN feed'

	feedRSS = xmlgen.XMLEnclosedTag('rss')
	feedRSS.addAttrib('version', RSSVersion)
	feedRSS.addAttrib('xmlns:xsi', XSI)
	feedRSS.addAttrib('xmlns:media', XMLNS)
	feedTitle = xmlgen.XMLEnclosedTag('title')
	feedTitle.addContent(title)
	feedChannel = xmlgen.XMLEnclosedTag('channel')
	feedLink = xmlgen.XMLEnclosedTag('link')
	feedLink.addContent(link)
	feedDescription = xmlgen.XMLEnclosedTag('description')
	feedDescription.addContent(description)

	feedRSS.addChildTag(feedChannel)
	feedChannel.addChildTag(feedTitle)
	feedChannel.addChildTag(feedLink)
	feedChannel.addChildTag(feedDescription)
	
	numberOfPosts = 25
	numberPosted = 0
	
	items = os.listdir(path = 'items/')
	items.sort(reverse = True)
	for item in items:
		if numberPosted < numberOfPosts:
			with open('items/' + item, 'r') as itemXMLFile:
				itemXML = itemXMLFile.read()
				feedChannel.addContent(itemXML)
			numberPosted += 1

	return feedRSS.publish().encode('utf-8')

def demo(item):
	RSSVersion = '2.0'
	XSI = 'http://www.w3.org/2001/XMLSchema-instance'
	XMLNS = 'http://search.yahoo.com/mrss/'
	title = 'Preview RSS Entry'
	link = 'http://172.16.1.150/'
	description = 'Posting preview'

	feedRSS = xmlgen.XMLEnclosedTag('rss')
	feedRSS.addAttrib('version', RSSVersion)
	feedRSS.addAttrib('xmlns:xsi', XSI)
	feedRSS.addAttrib('xmlns:media', XMLNS)
	feedTitle = xmlgen.XMLEnclosedTag('title')
	feedTitle.addContent(title)
	feedChannel = xmlgen.XMLEnclosedTag('channel')
	feedLink = xmlgen.XMLEnclosedTag('link')
	feedLink.addContent(link)
	feedDescription = xmlgen.XMLEnclosedTag('description')
	feedDescription.addContent(description)

	feedRSS.addChildTag(feedChannel)
	feedChannel.addChildTag(feedTitle)
	feedChannel.addChildTag(feedLink)
	feedChannel.addChildTag(feedDescription)
	
	feedChannel.addContent(item)

	return feedRSS.publish().encode('utf-8')
