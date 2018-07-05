#coding=utf-8

import requests
import threading
import url_base
def host(url):
	url = url.split('?')[0]
	url =  url.split("://")[-1]
	url = url.split("/")[0]
	return url 
def phost(url):
	url = url.split('?')[0]
	urls =  url.split("://")
	url = urls[-1]
	px = ""
	if len(urls)==2:
		px=urls[0]+"://"
	url = url.split("/")[0]
	return px+url 
class Robots(object):
	lock = threading.Lock()
	maps = {}
	locked = True
	def __init__(self,locked=True):
		self.locked = locked
		self.maps = {}
	#@staticmethod
	def check_host(self,url):
		hst = host(url)
		maps = self.maps 
		if not self.locked:
			exist = hst in maps 
		else:
			with Robots.lock:
				exist = hst in maps 
		if not exist:
			rst = robots(url)
			if not self.locked:
				maps[hst] = rst
			else:
				with Robots.lock:
					maps[hst] = rst
		
	#@staticmethod
	def allow(self,url,user_agent="*"):
		hst = host(url)
		maps = self.maps
		self.check_host(url)
		return allow(maps[hst],url,user_agent)
	#@staticmethod 
	def delay(self,url, user_agent = '*'):
		user_agent = ''.join(user_agent.split(" "))
		hst = host(url)
		maps = self.maps
		self.check_host(url)
		robots = maps[hst]
		if user_agent not in robots:
			user_agent = "*"
		if user_agent not in robots:
			return 0
		return robots[user_agent]['crawl-delay']
show = False		
def robots(url):
	url = phost(url) + "/robots.txt"
	outs = {}
	uname = ""
	kv = ""
	try:
		rp=requests.get(url,headers=url_base.header(),timeout = 5.0)
		rp.encoding = 'utf-8'
		contents = rp.text.lower()
		#print "robotss:",contents
		contents = "".join(contents.split(" "))
		#print "Robots:",contents
		user_agent = "user-agent"
		if contents.count(user_agent)==0 or contents[0] == '<':
			#print "bad robots.txt"
			return outs
		user_agents = contents.split("user-agent:")[1:]
		#print "num of ua:",len(user_agents)
		for user_agent in user_agents:
			lst = "".join(user_agent.split("\r")).split("\n")
			uname = lst[0]
			lst = lst[1:]
			outs[uname]={'disallow':[],'allow':[],'sitemap':[],'crawl-delay':0}
			for it in lst:
				if it == "" or it[0] == "#":
					continue 
				kv = it.split(':')
				if len(kv)<2:
					continue
				if kv[0] not in ['disallow','allow','sitemap','crawl-delay']:
					continue
				if kv[0] != "crawl-delay":
					outs[uname][kv[0]].append(":".join(kv[1:]))
				else:
					outs[uname][kv[0]]=int(kv[1])
		return outs			
	except Exception,e:
		global show
		if not show:
			return outs
		print "error:",e, url
		print "KEY:",uname,kv
		#return outs
		try:
			import traceback
			traceback.print_exc()
		except:
			print "Can't use module traceback to show details"
		return outs
def allow(robots,url,user_agent="*"):
	user_agent = ''.join(user_agent.split(" "))
	hst = phost(url)
	url = url[len(hst):]
	if user_agent not in robots:
		user_agent = "*"
	if user_agent not in robots:
		return True
	mp = robots[user_agent]
	allows = mp['allow']
	disallows = mp['disallow']
	for rule in disallows:
		if url.find(rule)==0:
			return False 
	for rule in allows:
		if url.find(rule)==0:
			return True 
	return len(allows)==0