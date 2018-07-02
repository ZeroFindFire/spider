#coding=utf-8

import requests
import threading

class Robots(object):
	lock = threading.Lock()
	maps = {}
	@staticmethod
	def check_host(url):
		hst = host(url)
		maps = Robots.maps 
		with Robots.lock:
			exist = hst in maps 
		if not exist:
			rst = robots(url)
			with Robots.lock:
				maps[hst] = rst
		
	@staticmethod
	def allow(url,user_agent="*"):
		hst = host(url)
		maps = Robots.maps
		Robots.check_host(url)
		return allow(maps[hst],url,user_agent)
	@staticmethod 
	def delay(url, user_agent = '*'):
		hst = host(url)
		maps = Robots.maps
		Robots.check_host(url)
		robots = maps[hst]
		if user_agent not in robots:
			user_agent = "*"
		if user_agent not in robots:
			return 0
		return robots[user_agent]['crawl-delay']
			
def robots(url):
	url = phost(url) + "/robots.txt"
	outs = {}
	uname = ""
	kv = ""
	try:
		rp=requests.get(url,header(),timeout = 5.0)
		rp.encoding = 'utf-8'
		contents = rp.text.lower()
		#print "robotss:",contents
		contents = "".join(contents.split(" "))
		#print "Robots:",contents
		user_agent = "user-agent"
		if contents.count(user_agent)==0 or contents[0] == '<':
			return outs
		user_agents = contents.split("user-agent:")[1:]
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
		return outs
		print "error:",e, url
		print "KEY:",uname,kv
		try:
			import traceback
			traceback.print_exc()
		except:
			print "Can't use module traceback to show details"
		return outs
def allow(robots,url,user_agent="*"):
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