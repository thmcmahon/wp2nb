import simplejson as json
import xmltodict
import requests
import os
import re
import sys
import base64
from urlparse import urlparse
from os.path import splitext, basename

nb_token = os.environ.get('NB_TOKEN')

def youtube_links(input):
	''' Find youtube links in any wordpress blogpost'''
	# This is some horrible regex, see
	# http://stackoverflow.com/questions/839994/extracting-a-url-in-python
	url = re.findall(r'(src=\S+)', input)
	if len(url) > 0:
		url = url[0]
		url = url.replace('src=', '')
		url = url.replace('"', '')
		# The URL format for youtube videos changed halfway through the life of the blog, this tests for the format and returns the correct URL
		if url.startswith("//"):
			# If it's the new broken format append http, otherwise just return the URL
			url = "http:" + url
			return url
		else:
			return url

def read_xml(input_xml):
	''' Reads an xml file and turns it into a dictionary '''
	f = open(input_xml, 'r')
	doc_xml = f.read()
	doc = xmltodict.parse(doc_xml)
	return doc

def convert_wp2nb(input_xml):
	''' Extracts the relevant items from wordpress posts and converts it into a nationbuilder friendly
	format. If there are any youtube links it appends them to the end of the post '''
	content = input_xml['content:encoded']
	if content is not None:
		content = content.replace('\n', '<br>')
		if content.find('youtube') > 0:
			youtube_url = youtube_links(content)
			if youtube_url is not None:
				content = content + youtube_url
		output_dict = {'blog_post': {'name': input_xml['title'], 'slug': input_xml['wp:post_id'], 'status': 'published', 'content_before_flip': content, 'published_at': input_xml['pubDate'], 'author_id': '2'}}
	else:
		output_dict = {'blog_post': {'name': input_xml['title'], 'slug': input_xml['wp:post_id'], 'status': 'published', 'content_before_flip': input_xml['content:encoded'], 'published_at': input_xml['pubDate'], 'author_id': '2'}}
	json_output = json.dumps(output_dict)
	return json_output

def nb_upload(input_json):
	''' Uploads blog posts to the nationbuilder URL '''
	url = 'https://andrewleigh.nationbuilder.com/api/v1/sites/andrewleigh/pages/blogs/1/posts'
	payload = input_json
	headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
	parameters = {'access_token': nb_token}
	r=requests.post(url, data=payload, headers=headers, params=parameters)
	response = r.status_code
	print response

def delete_post(id):
	''' Delete a nationbuilder post '''
	url = 'https://andrewleigh.nationbuilder.com/api/v1/sites/andrewleigh/pages/blogs/1/posts/%s' % id
	headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
	parameters = {'access_token': nb_token}
	r=requests.delete(url, headers=headers, params=parameters)
	response = r.status_code
	print response

def get_posts():
	''' Get blog post IDs '''
	url = 'https://andrewleigh.nationbuilder.com/api/v1/sites/andrewleigh/pages/blogs/1/posts/'
	headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
	parameters = {'access_token': nb_token, 'per_page': '100'}
	r=requests.get(url, headers=headers, params=parameters)
	response = json.loads(r.content)
	return response

def upload_image(page_slug, image_url):
	''' Upload an image attachment to a blog post '''
	url = 'https://andrewleigh.nationbuilder.com/api/v1/sites/andrewleigh/pages/%s/attachments' % page_slug
	image = prepare_image(image_url)
	headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
	parameters = {'access_token': nb_token}
	r=requests.post(url, headers=headers, params=parameters, data=json.dumps(image))
	return r

def prepare_image(url):
	''' Downloads an image, encodes it to base64 for the NB api and sets required parameters then returns a dictionary '''
	# Download the image then enode it as bas364 per the NB api requirements
	image = requests.get(url)
	image_base64 = base64.b64encode(image.content)
	# This splits the filename from the URL. See http://stackoverflow.com/questions/10552188/python-split-url-to-find-image-name-and-extension
	image_disassembled = urlparse(image.url)
	filename, file_ext = splitext(basename(image_disassembled.path))
	image_filename = filename[1:] + file_ext
	content = {'attachment': {'filename': image_filename, 'content_type': 'image/jpeg', 'updated_at': '2013-06-06T10:15:02-07:00', 'content': image_base64}}
	return content

if __name__ == "__main__":
	# This needs to be replaced by using sysargv
	input_file = sys.argv[1]
	doc = read_xml(input_file)
	for i in doc['rss']['channel']['item']:
		json_output = convert_wp2nb(i)
		nb_upload(json_output)

	
