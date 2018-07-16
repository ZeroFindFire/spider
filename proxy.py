#coding=utf-8
import requests 
import bs4 
from multi import multi 
import rsp
import threading
import time
import socks 
import socket 
socket.socket = socks.socksocket
"""

python
from spider import proxy
outs= proxy.proxy()
sks=proxy.sock_proxy(outs)
csks = proxy.checked_socks(sks)

"""
def to_url(proxy):
	return "http://"+proxy['ip']+":"+proxy['port']
def to_proxies(proxy):
	return {proxy['type']:"http://"+proxy['ip']+":"+proxy['port']}
	
def check(proxy):
	proxies = deal(proxy)
	url = proxy['type']+"://www.baidu.com"
	if proxy['type'] not in ['http','https']:
		print "not http type",proxy['type']
		return False
	try:
		rp=requests.get(url,proxies=proxies)
	except Exception,e:
		print "except",e
		return False 
	return rp 
url = "http://www.xicidaili.com/"
def proxy(url=url):
	headers = { 'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'  }
	headers['Refere'] = url
	response = requests.get(url,headers = headers)
	response.encoding = "utf-8"
	soup = bs4.BeautifulSoup(response.text,"html.parser")
	rst_odd = soup.find_all("tr",attrs = {'class':'odd'})
	rst = soup.find_all("tr",attrs = {'class':''})
	rst = [obj for obj in rst if obj.has_attr('class')]
	rst+=rst_odd
	outs = []
	for obj in rst:
		tds = obj.find_all('td')
		ip = str(tds[1].string)
		port = str(tds[2].string)
		dest = tds[3].string
		ptype = str(tds[5].string).lower()
		outs.append({'ip':ip,'port':port,'address':dest,'type':ptype})
	return outs
def sock_proxy(outs):
	rst = []
	for obj in outs:
		if obj['type'].find("sock")>=0 and obj['type'].find("5")>=0:
			rst.append(obj)
	return rst 
def checked_socks(proxys):
	rst = []
	for proxy in proxys:
		if not check_sock(proxy):
			continue 
		rst.append(proxy)
	return rst 

def bind_sock_proxy(sockobj,proxy):
	sockobj.setproxy(socks.PROXY_TYPE_SOCKS5, proxy['ip'],proxy['port'])
	return sockobj 
def default_sock_proxy(proxy):
	socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5,proxy['ip'],proxy['port'])
	socket.socket = socks.socksocket 
def check_sock(proxy, url = url):
	default_sock_proxy(proxy)
	try:
		rp=requests.get(url)
		return True
	except Exception,e:
		print "except",e
		return False
check_lock = threading.Lock()
def check_sock_lock(proxy):
	global check_lock
	with check_lock:
		return check_sock(proxy)

class Proxy(threading.Thread):
	def __init__(self, update_time = 10.0):
		threading.Thread.__init__(self)
		self.__running = True
		self.proxy = None 
		self.update_time = update_time
	def poweroff(self):
		self.__running = False
	def on_running(self):
		return self.__running
	def update(self):
		source = proxy()
		spd = ProxyCheck(source)
		spd.run()
		self.proxy = spd
		self.outs = spd.outs
		self.http = self.outs['http']
		self.https = self.outs['https']
	def start(self):
		self.update()
		threading.Thread.start(self)
	def run(self):
		while self.__running:
			self.update()
			time.sleep(self.update_time)
	def rand(self):
		if self.proxy is not None:
			return self.proxy.rand()
		else:
			return None


"""
class ProxyCheck(multi.Multi):
	timeout = 5.0
	show = False
	def __init__(self,proxies):
		multi.Multi.__init__(self,True)

		self.lock = threading.Lock()
		self.outs = {'http':[],'https':[],'socks4/5':[]}
		self.urls = []
		for px in proxies:
			if px['type'] not in self.outs.keys():
				continue
			url = px['type']+"://www.baidu.com" 
			mp = {"url" : url, 'proxies' : to_proxies(px), 'remain' : px}
			self.urls.append(mp)
	def deal(self, response, remain):
		if type(response) in [str, unicode]:
			return
		with self.lock:
			self.outs[remain['type']].append(remain)
	def clean(self):
		return self.outs
	def rand(self):
		import random 
		http, https = list(self.outs['http']), list(self.outs['https'])
		maps = {}

		if len(http) > 0:
			http_proxy = to_url(http[random.randint(0,len(http)-1)])
			maps['http'] = http_proxy

		if len(https) > 0:
			https_proxy = to_url(https[random.randint(0,len(https)-1)])
			maps['https'] = https_proxy
		return maps
		"""
"""
python
from spider import proxy as px
outs = px.proxy()
spd = px.Proxy(outs)
tmp = spd.run()

python
from spider import proxy as px
spd = px.Proxy()
spd.start()

check(outs[0])
"""