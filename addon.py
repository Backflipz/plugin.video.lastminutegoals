from xbmcswift2 import Plugin
import os
import sys
import xbmc
from bs4 import BeautifulSoup as BS
import requests
import re
plugin = Plugin()

lib = 'special://home' + '/addons/' + plugin._addon_id+'/'
@plugin.route('/')
def index():
    items = [{
        'label': 'Search...',
        'path': plugin.url_for('search')
    },
	{
		'label': 'UEFA Champions League',
		'path': plugin.url_for('cats',cat = 'uefa-champions-league',page = '1'),
		'properties': {'Fanart_Image':lib+'ucl.jpg'},
		'thumbnail': lib+'ucl_icon.jpg'
	},
	{
		'label': 'UEFA Europa League',
		'path': plugin.url_for('cats',cat = 'uefa-europa-league',page = '1'),
		'properties': {'Fanart_Image':lib+'europa.jpg'},
		'thumbnail': lib+'europa_icon.png'
	},
	{
		'label': 'UEFA Euro 2016',
		'path': plugin.url_for('cats',cat = 'euro-2016',page = '1'),
		'properties': {'Fanart_Image':lib+'euro2016.png'},
		'thumbnail': lib+'euro2016_icon.jpg'
	},
	{
		'label': 'International',
		'path': plugin.url_for('cats',cat = 'international',page = '1'),
		'properties': {'Fanart_Image':lib+'international.jpg'},
		'thumbnail': lib+'fifa_icon.png'
	},
	{
		'label': 'Premier League',
		'path': plugin.url_for('cats',cat = 'premier-league',page = '1'),
		'properties': {'Fanart_Image':lib+'premier.jpg'},
		'thumbnail': lib+'plg_icon.png'
	},
	{
		'label': 'La Liga',
		'path': plugin.url_for('cats',cat = 'la-liga-2',page = '1'),
		'properties': {'Fanart_Image':lib+'liga.jpg'},
		'thumbnail': lib+'liga_icon.jpg'
	},
	{
		'label': 'Bundesliga',
		'path': plugin.url_for('cats',cat = 'bundesliga',page = '1'),
		'properties': {'Fanart_Image':lib+'bundesliga.jpg'},
		'thumbnail': lib+'b_icon.png'
	},
	{
		'label': 'Serie A',
		'path': plugin.url_for('cats',cat = 'seriea',page = '1'),
		'properties': {'Fanart_Image':lib+'seriea.jpg'},
		'thumbnail': lib+'s_icon.png'
	},
	{
		'label': 'Ligue 1',
		'path': plugin.url_for('cats',cat = 'ligue1',page = '1'),
		'properties': {'Fanart_Image':lib+'ligue.jpg'},
		'thumbnail': lib+'ligue_icon.png'
	},
	{
		'label': 'Eredivisie',
		'path': plugin.url_for('cats',cat = 'eredivisie',page = '1'),
		'properties': {'Fanart_Image':lib+'eredivisie.jpg'},
		'thumbnail': lib+'e_icon.png'
	},
	{
		'label': 'Liga Zon Sagres',
		'path': plugin.url_for('cats',cat = 'liga-zon-sagres',page = '1'),
		'properties': {'Fanart_Image':lib+'ligazon.jpg'},
		'thumbnail': lib+'l_icon.png'
	},
	{
		'label': 'MLS',
		'path': plugin.url_for('cats',cat = 'mls',page = '1'),
		'properties': {'Fanart_Image':lib+'mls.jpg'},
		'thumbnail': lib+'mls_icon.png'
	}]
    return items

@plugin.route('/page_options/<url>/')
def transform_page(url):
	lmg = requests.get(url)
	soup = BS(lmg.text)
	items = []
	index = 0
	for link in soup.find_all('article')[0].find_all('a'):
		item = {}
		url = link['href']
		item['label'] = link.string
		if 'tabs' in url and ('stats' not in str(link.string).lower()):  
			item['path'] = plugin.url_for('play_page',url = url, index = index)
			index+=1
			items.append(item)
	return items
	
@plugin.route('/play_page/<index>/<url>/')
def play_page(url,index):
	from bs4 import NavigableString,Tag
	lmg = requests.get(url)
	soup = BS(lmg.text)
	items = []
	plugin.log.info('TITLE %s' % soup.title)
	textAppr = 0
	for link in soup.find_all('p')[int(index)]:
		link_txt = str(link.string).replace('\n','').replace('\r','')
		plugin.log.info('LINK TXT %s' % link.string)
		# if (link_txt != '') and (link_txt != 'None') and ('meme' not in link_txt):
			# ne = link.next_element
			# while 1:
				# if 'script' in str(ne):
					# break
				# ne = ne.next_element
			# plugin.log.info('NE %s' % str(ne))
			# try:
				# try: pc = playwire_config('http:' + ne['data-config'])
				# except: pc = playwire_config(ne['data-config'])
			# except: pc = playwire_config(ne.script['data-config'])
			# plugin.log.info(pc)
			# item = {'label': link_txt + ' (%s)' % pc['duration'], 
			# 'path': pc['url'],
			# 'info' : {'title':soup.title.string},
			# 'thumbnail': pc['thumbnail'],
			# 'is_playable': True}
			# items.append(item)
			# textAppr = 1
		if isinstance(link,Tag):
			try:
				try: pc = playwire_config('http:' + link['data-config'])
				except: pc = playwire_config(link['data-config'])
				plugin.log.info(pc)
				item = {'label': pc['title'] + ' (%s)' % pc['duration'], 
				'path': pc['url'],
				'info' : {'title':soup.title.string},
				'thumbnail': pc['thumbnail'],
				'is_playable': True}
				items.append(item)
			except:pass
			
	return items

			
def playwire_config(url):
	pwire = requests.get(url).json()
	plugin.log.info('PWIRE %s' % pwire)
	try: xml = requests.get(pwire['content']['media']['f4m'])
	except: xml = requests.get(pwire['src'])
	soup = BS(xml.text)
	play_url = soup.baseurl.string + '/' + soup.media['url']
	try: img = pwire['content']['poster']
	except: img = pwire['poster']
	duration = int(soup.duration.string)
	sec = duration%60
	if sec < 10: sec = '0'+str(sec)
	duration = '%s:%s' % (duration/60, sec)
	try: title = pwire['settings']['title']
	except: title = pwire['title']
	return {'url': play_url, 'thumbnail':img, 'duration': duration, 'title':title}

@plugin.route('/search/<search_term>/<page>/', name = 'search_one')
@plugin.route('/search/')
def search(search_term = '',page = '1'):
	if len(search_term) == 0:
		search_term = plugin.keyboard(heading = 'Enter Search Term')
	
	url = 'http://www.lastminutegoals.org/page/%s/?s=%s' % (page,search_term)
	
	lmg = requests.get(url)
	soup = BS(lmg.text)
	items = []
	for link in soup.find_all('article'):
		l_url = link.a['href']
		title = link.a.img['alt'] + ' (%s)' % l_url[31:41]
		img = 'http://' + link.a.img['src'][2:]
		img = img.replace('-110x110','')
		item = {'label': title, 'thumbnail' : img, 'path':plugin.url_for('transform_page',url = l_url)}
		items.append(item)
	items.append({'label':'Next Page >>>', 'path':plugin.url_for('search_one',page = str(int(page)+1),search_term=search_term)})
	return items

@plugin.route('/cats/<cat>/<page>/')
def cats(cat = '', page = '1'):
	url = 'http://www.lastminutegoals.org/category/highlights/%s/page/%s/' % (cat, page)
	
	lmg = requests.get(url)
	soup = BS(lmg.text)
	items = []
	for link in soup.find_all('article'):
		l_url = link.a['href']
		title = link.a.img['alt'] + ' (%s)' % l_url[31:41]
		img = 'http://' + link.a.img['src'][2:]
		img = img.replace('-110x110','')
		item = {'label': title, 'thumbnail' : img, 'path':plugin.url_for('transform_page',url = l_url)}
		items.append(item)
	items.append({'label':'Next Page >>>', 'path':plugin.url_for('cats',page = str(int(page)+1),cat=cat)})
	return items
if __name__ == '__main__':
    plugin.run()
