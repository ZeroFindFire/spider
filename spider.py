#coding=utf-8
   
import socket
import time
import threading
import re
import requests
from multi import multi
import url_base

def act():
	return threading.active_count()
# set socket timeout
def timeout(sec):
	global global_timeout
	global_timeout = sec 
	socket.setdefaulttimeout(global_timeout)
global_timeout=None

# A description, notes: the class that you should inherit is Spider, not BaseSpider
class BaseSpider(object):

	# init urls to spiding 
	urls = []
	# default timeout for get and post
	timeout = None
	# max threads limit 
	max_threads = 300
	# http type
	action="get" # get, post, head...
	# time seperate of each spiding 
	seperate_time = 0
	show = True
	container_size = 300
	# you should implement this by yourself
	def deal(self, response, remain, succeed):
		pass
	
	# you can implement this 
	def clean(self):
		pass
	
	# 
	def suspend(self):
		pass 
	
	# 
	def resume(self):
		pass
	
	# append url to spider
	def push(self, url, action = None, maps = dict(), remain = None):
		pass
	
	# filter url, True: spiding thid url, False: throw this url 
	def filter(self, url):
		return True
		
	# let spider running
	def start(self):
		pass
	
	# let spider running
	def work(self,asyn = False):
		pass

	# let spider stop running
	def poweroff(self):
		pass 
	
	# check if spider is really shutdown 
	def done(self):
		pass


#url, maps, remain, action
class Spider(multi.Multi):
	urls = []
	def __init__(self,urls = None):
		multi.Multi.__init__(self)
		if urls is not None:
			self.urls = urls
		self.init_urls()
	def init_urls(self):
		self.init_objs()
		for urlobj in self.urls:
			tp = type(urlobj)
			maps, remain, action = dict(), None, None
			if tp not in [dict,list,tuple]:
				url = urlobj 
			elif tp == dict:
				tmpobj = dict(urlobj)
				url = tmpobj['url']
				del tmpobj['url']
				if 'remain' in tmpobj:
					remain = tmpobj['remain']
					del tmpobj['remain']
				if 'action' in tmpobj:
					action = tmpobj['action']
					del tmpobj['action']
				maps=tmpobj
			else:
				url = urlobj[0]
				l = len(urlobj)
				if l > 1:
					maps = urlobj[1]
				if l > 2:
					remain = urlobj[2]
				if l > 3:
					action = urlobj[3]
			self.init_push(*self.__format_change(url, action, maps, remain))
	action = 'get'
	# append url to spider
	def __format_change(self, url, action = None, maps = dict(), remain = None):
		if 'timeout' not in maps:
			maps['timeout'] = self.timeout 		
		if action == None:
			action = self.action
		func = requests.__dict__[action]
		if 'headers' not in maps:
			maps['headers']=url_base.header(url)
		attrs = self.attrs([url],maps)
		remain = [url,remain]
		return func,attrs,remain,self.__deal
	
	def push(self, url, action = None, maps = dict(), remain = None):
		attrs = self.__format_change(url,action,maps,remain)
		multi.Multi.push(self,*attrs)
	def deal(self,response,remain,succeed):
		pass
	def __deal(self, response, remain, succeed):
		rp = response
		if succeed:
			ct=rp.content
			import re 
			pattern = 'charset=(.*?)>'
			rst=re.findall(pattern,ct)
			if (len(rst)>0):
				rst=rst[0].lower()
				if rst.find('utf-8')>=0:
					rp.encoding = 'utf-8'
				elif rst.find('gbk')>=0:
					rp.encoding = 'gbk'
				elif rp.encoding=='ISO-8859-1' and rst.find('iso-8859-1')<0:
					rp.encoding = 'gbk'
		remain = remain[1]
		self.deal(rp,remain,succeed)
