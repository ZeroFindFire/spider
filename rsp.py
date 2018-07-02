#coding=utf-8

# a old version used for proxy, don't used this, use spider.py instead
import urllib  
import urllib2    
import socket
import time
import threading
import re
import requests
def dctcmp(m0,m1):
	df=[]
	for i in m0:
		if i not in m1 or m0[i]!=m1[i]:
			df.append(i)
	for i in m1:
		if i not in m0:
			df.append(i)
	return df
def todict(cks):
	out = {}
	for ck in cks:
		out[ck['name']]=ck['value']
	return out

def strsfind(lst,s):
	o=[]
	for i in lst:
		if i.find(s)>=0:
			o.append(i)
	return o

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
def is_html(url):
	url=url.split("?")[0]
	rurl=url[::-1]
	if len(rurl)<=4:
		return False
	return True
	htmls=["html","htm","php","/","jpg","jpeg","gif","jsp","png"]
	for html in htmls:
		if rurl.find(html[::-1])==0:
			return True 
	return False
def html2urls(contents,base_url):
	import bs4
	soup=bs4.BeautifulSoup(contents,"html5lib")
	lnks=[ i for i in soup.descendants if type(i) == bs4.element.Tag and (i.has_attr('src') or i.has_attr('href'))]
	olnks=[ i.attrs['src'] for i in lnks if i.has_attr('src')] + [ i.attrs['href'] for i in lnks if i.has_attr('href')]
	lnks=[i for i in olnks if is_html(i)]
	outs=[]
	for lnk in lnks:
		url=fullurl(lnk,base_url)
		if url == None:
			continue 
		outs.append(url)
	return outs
def html2lnks(contents,base_url):
	import bs4
	soup=bs4.BeautifulSoup(contents,"html5lib")
	lnks=[ i for i in soup.descendants if type(i) == bs4.element.Tag and (i.has_attr('src') or i.has_attr('href'))]
	olnks=[ (i.attrs['src'],i.text,i) for i in lnks if i.has_attr('src')] + [ (i.attrs['href'],i.text,i) for i in lnks if i.has_attr('href')]
	lnks=[i for i in olnks if is_html(i[0])]
	outs=[]
	for lnk in lnks:
		url=fullurl(lnk[0],base_url)
		if url == None:
			continue 
		outs.append([url,lnk[1],lnk[2]])
	return outs

def act():
	return threading.active_count()
# set socket timeout
def timeout(sec):
	global global_timeout
	global_timeout = sec 
	socket.setdefaulttimeout(global_timeout)
sleep_time=1.0
global_timeout=None
#socket.setdefaulttimeout(global_timeout)
# data for get and post is a map
def get(url, data = None, refer = None, timeout = None):
	if data is not None:
		data = urllib.urlencode(data)
		url = url + "?" + data 
	return request(url, None, header(url, refer), timeout)

def post(url, data = None, refer = None, timeout = None):
	if data is not None:
		data = urllib.urlencode(data)
	return request(url, data, header(url, refer), timeout)


# A description, notes: the class that you should inherit is Spider, not BaseSpider
class BaseSpider(object):
	def str(self,obj):
		return obj in[str,unicode]
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
	def deal(self, response, remain = None):
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
	def push(self, url, action = None, maps = dict(), remain = None, force = False):
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
	
# fetch links from html context and deal links
# it's usefull if you want to get url links from context
def links(cts,url):
	sets=set()
	urls=fetch(cts)
	urls=fullurls(urls,url)
	for turl in urls:
		sets.add(turl)
	return sets

# fetch links from html context 
# not recommend to use
def fetch(cts):
	urls=re.findall(pattern,cts)
	outs=[]
	for url in urls:
		outs.append(url[2]+url[3])
	return outs 

pattern="(href|src)=('([^']*)'|\"([^\"]*)\")"

def header( refer = None):
	user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' 
	user_agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36';
	headers = { 'User-Agent' : user_agent }
	if refer is not None:
		headers['Refere'] = refer
	return headers

user_agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36';
def request(url, data, headers, time_out = None):
	global global_timeout
	if time_out is None:
		time_out = global_timeout
	try:
		request = urllib2.Request(url, data, headers)  
		if timeout is None:
			response = urllib2.urlopen(request) 
		else: 
			response = urllib2.urlopen(request, timeout = time_out) 
		return response
	except:
		return url

class SpiderThread(threading.Thread):
	def __init__(self, url, maps, remain, spider):
		threading.Thread.__init__(self)
		self.maps = maps 
		self.spider = spider
		self.url = url
		self.__done = False 
		self.remain = remain
	def done(self):
		return self.__done
	
	def run(self):
		func=requests.__dict__[self.maps["action"]]
		try:
			#rp = func(self.url, data = self.data, cookies = self.cookies, headers = self.headers, timeout = self.timeout)
			order = "rp=func(self.url"
			maps = self.maps
			for key in maps:
				if key != "action":
					order += ", "+key+"=maps['"+key+"']"
			order+=")"
			#print "exec:",order
			exec(order)
		except Exception,e:
			if self.spider.show:
				print "ERROR in thread run:",e
				print "ORDER:",order
				print "URL:",self.url
				import traceback
				traceback.print_exc()
			rp = str(self.url)
		if rp == None:
			rp = str(self.url)
		#with type(self).lock:
		#	print "RESPONSE:<<<<<",rp,self.url,">>>>>>"
		try:
			if type(rp) not in[str,unicode]:
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
			self.spider.deal(rp,self.remain)
		except Exception,e:
			print "There are Error in your codes:", e
			try:
				import traceback
				traceback.print_exc()
			except:
				print "Can't use module traceback to show details"
		self.__done = True
	
class MainThread(threading.Thread):
	def __init__(self, spider):
		threading.Thread.__init__(self)
		self.spider =spider 
	
	def run(self):
		self.spider.inner_run()
		self.spider.thd_done()


class Spider(BaseSpider):
	def __init__(self):
		self.__on_running = False
	def change_run_urls(self):
		self.__run_urls = self.__wait_urls[0]
		self.__wait_urls = self.__wait_urls[1:]
		if len(self.__wait_urls)==0:
			self.__wait_urls.append([])
		
	def __initz(self):
		self.__suspended=False
		self.__lock = threading.Lock()
		self.__suspend_lock = threading.Lock()
		self.__run_urls = []
		self.__wait_urls = [[]]
		self.__history=set()
		for urlobj in self.urls:
			tp = type(urlobj)
			remain = None
			if tp != dict:
				url = urlobj 
				maps = dict()
			else:
				tmpobj = dict(urlobj)
				url = tmpobj['url']
				del tmpobj['url']
				if 'remain' in tmpobj:
					remain = tmpobj['remain']
					del tmpobj['remain']
				maps=tmpobj
			self.push(url, maps, remain)
			#self.__run_urls.append((url, maps, remain))
		self.change_run_urls()
	
	def push(self, url, maps = dict(), remain = None, force = False):
		with self.__lock:
			if force or (url not in self.__history and url not in self.__history):
				if len(self.__wait_urls[-1])>= self.container_size:
					self.__wait_urls.append([])
					#print 'add wait_urls'
				self.__wait_urls[-1].append((url, maps, remain))
				#print "push",url,len(self.__wait_urls[-1])

	def start(self):
		if self.__on_running:
			return False
		self.__stop = False
		self.__on_running = True
		main_thread = MainThread(self)
		main_thread.start()
		self.__main_thread = main_thread
		return self.__on_running

	def work(self,asyn = True):
		if asyn:
			return self.start()
		else:
			return self.run()
	
	def poweroff(self):
		self.__stop=True
	
	def done(self):
		return self.__on_running==False
	
	def thd_done(self):
		self.__on_running=False
	
	def resume(self):
		if not self.__suspended:
			return True 
		self.__suspend_lock.release()
		self.__suspended = False 
		return True
	
	def suspend(self):	
		if self.__suspended:
			return True
		self.__suspend_lock.acquire()
		while len(self.__threads)>0:
			th=self.__threads[0]
			th.join()
			if th.done():
				self.__threads.pop(0)
		self.__suspended = True
		return True
	def clear_threads(self):
		len_thd = len(self.__threads)
		cnt_thd = 0
		while cnt_thd < len_thd:
			if self.__threads[cnt_thd].done():
				self.__threads.pop(cnt_thd)
				len_thd -= 1
			else:
				cnt_thd += 1
	def run(self):
		self.__stop = False
		out = self.inner_run()
		self.__on_running=False
		return out

	def inner_run(self):
		action = self.action
		self.__initz()
		self.__threads = []
		global sleep_time
		#cnt=0
		while (len(self.__run_urls) + len(self.__threads)) > 0 and not self.__stop:
			#if cnt >= 1000:
			#	cnt=0
			#	print "LOOP"
			self.__history.update([url for url, maps, remain in self.__run_urls])
			cls_cnt=0
			if len(self.__run_urls) == 0:
				if self.timeout is not None:
					time.sleep(self.timeout)
				else:
					time.sleep(sleep_time)
				
			for obj in self.__run_urls:
				if self.seperate_time>0:
					if self.show:
						print "sleep for seperate_time"
					time.sleep(self.seperate_time)
				url, maps, remain = obj 
				if self.filter(url)==False:
					continue					
				if "action" not in maps:
					maps["action"] = action 
				if 'timeout' not in maps:
					maps['timeout'] = self.timeout 		
				if "headers" not in maps:
					maps["headers"] = header(url) 
				while threading.active_count() >= self.max_threads:
					if self.show:
						print "sleep for active_count()"
					if self.timeout is not None:
						time.sleep(min(self.timeout,5))
					else:
						time.sleep(sleep_time)
				cls_cnt+=1
				if cls_cnt>=self.max_threads:
					self.clear_threads()
					cls_cnt=0
				newthread=None
				with self.__suspend_lock:
					while newthread is None:
						try:
							newthread = SpiderThread(url, maps, remain, self)
							newthread.start()
						except Exception,e:
							if self.show:
								print "create or start thread error:",e,e.message
							newthread=None 
							time.sleep(sleep_time)
					if newthread is not None:
						self.__threads.append(newthread)
			with self.__lock:
				self.change_run_urls()
				#print "exchange run_urls",len(self.__run_urls),len(self.__wait_urls),len(self.__wait_urls[-1])
			self.clear_threads()
		while len(self.__threads)>0:
			th=self.__threads[0]
			th.join()
			if th.done():
				self.__threads.pop(0)
		try:
			return self.clean()
		except Exception, e:
			print "Error code in your spider's function clean:", e 
			try:
				import traceback
				traceback.print_exc()
			except:
				print "Can't use module traceback to show details"
		return None


class DomainFilterSpider(Spider):
	domain_limit=[]
	def filter(self,url):
		for domain in domain_limit:
			l=len(domain.split("."))
			hst=host(url,l)
			if hst==domain:
				return True 
		return False

def run(spider):
	spider.start()

def clear_threads(threads,lv=0.5):
	len_thd = int(len(threads)*lv)
	cnt_thd = 0
	while cnt_thd < len_thd:
		if threads[cnt_thd].done():
			threads.pop(cnt_thd)
			len_thd -= 1
		else:
			cnt_thd += 1
	return len(threads)
def nourl(url):
	url=url.split("?")[0]
	#pattern="([^a-zA-Z0-9\./:_#]*)"
	#rst=re.findall(pattern,url)
	#for i in rst:
	#	if i!='':
	#		return True
	#tmp=url.split('.')
	#if len(tmp)<=1:
	#	return True
	js='javascript'
	if len(url)==0 or url[:len(js)]==js or url[0]=='#' or url[0]=='"' or url[0]=="'":
		return True 
	return False

def path_cmb(paths):
	out=""
	for path in paths:
		out+="/"+path 
	if out!="":
		out=out[1:]
	return out

def reduce(url):
	cnt=url.count("..")
	if cnt==0:
		return url 
	phst = phost(url)
	url = url[len(phst):]
	if url[0]=='/':
		url = url[1:]
	urls=url.split("..")
	page = urls[-1]
	urls = urls[:-1]
	bases=[phst]
	for path in urls:
		path=path.split("/")
		if path[0]=='':
			path = path[1:]
		if len(path)==0:
			continue
		if path[-1]== '':
			path = path[:-1]
		bases+=path 
		bases=bases[:-1]
	url = path_cmb(bases)+page
	url = ''.join(url.split('/.'))
	return url
def prefix(url):
	url=url.split("?")[0]
	pfx = ''
	if url.count('://')>0:
		pfx = url.split("://")[0]
	return pfx
def host(url,nodes=-1):
	prefix=""
	url=url.split("?")[0]
	if url.count('://')>0:
		tmp=url.split('://')
		prefix=tmp[0]+"://"
		url=tmp[1]
	_host=url.split('/')[0]
	if nodes>0:
		hosts=_host.split(".")
		_host=""
		for i in xrange(min(nodes,len(hosts))):
			_host=hosts[-i-1]+"."+_host
		_host=_host[:-1]
	return _host
def phost(url):
	hst = host(url)
	pfx = prefix(url)
	url = hst 
	if pfx != '':
		url = pfx + "://" + hst 
	return url
deal_url = {}
def fullurl(url,base):
	global deal_url
	backurl = url 
	backbase = base
	outs=[]
	prefix=base.split(":")[0]
	base_url=base.split("?")[0]
	last_url=base_url.split("/")[-1]
	if last_url == '':
		base_path = base_url
	else:
		base_path=base_url[:-len(last_url)]
	base_url=host(base_url)
	if nourl(url):
		return None
	elif url.find(':')>=0:
		pass
	elif url[:2]=="//":
		url=prefix+":"+url 
	elif url[0]=='/':
		url=prefix+"://"+base_url+url 
	else:
		url=base_path+url 
	url=reduce(url)
	deal_url[url]=(backurl,backbase)
	return url

def fullurls(urls,base):
	outs=[]
	prefix=base.split(":")[0]
	base_url=base.split("?")[0]
	last_url=base_url.split("/")[-1]
	base_path=base_url[:-len(last_url)]
	base_url=host(base_url)
	for url in urls:
		if nourl(url):
			continue 
		elif url.find(':')>=0:
			pass
		elif url[:2]=="//":
			url=prefix+":"+url 
		elif url[0]=='/':
			url=prefix+":"+base_url+url 
		else:
			url=base_path+url 
		url=reduce(url)
		outs.append(url)
	return outs

def page(url):
	url=url.split("?")[0]
	if url[-1]=='/':
		return '/'
	url=url.split('/')[-1]
	if url=='':
		url="index.html"
	return url


def suffix(page):
	page=page.split('.')[-1]
	return page

def ispage(ct_type):
	page_types=["text/html"]
	for pg_type in page_types:
		if ct_type.find(pg_type)>=0:
			return True 
	return False

def htmlurl(url):
	page=urlbase(url)
	sfx=suffix(page)
	return sfx in ['/','html','htm','php','']
"""
python
	
import threading as th

def tm(fc,*args):
	import time 
	st=time.time()
	rst=fc(*args)
	ed=time.time()
	return rst,ed-st

class Th(th.Thread):
	def __init__(self,sec=0.1):
		th.Thread.__init__(self)
		self.sec=sec 
	def run(self):
		import time 
		time.sleep(self.sec)

def test(num=3000,sec=0.1):
	for i in xrange(num):
		try:
			thd=Th(sec)
			thd.start()
		except Exception,e:
			#print "error",
			pass 
	print "ACTIVE COUNT:",th.active_count()

def tmtst(num=3000,sec=0.1):
	rst=tm(test,num,sec)
	print num/rst[1]

tmtst(5000,0.14)
def fd(objs,url):
	i=0
	rst=0
	for obj in objs:
		turl=obj[0]
		if turl==url:
			rst=i
		i+=1
	return rst
	
tm(fd,urls,threads[-1].url)
"""
