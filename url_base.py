#coding=utf-8
def rq_encode(response):
	rp = response
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
	return response
# cookies format from selinium to requests
def cookie_change(cks):
	out = {}
	for ck in cks:
		out[ck['name']]=ck['value']
	return out

def maybe_html(url):
	url=url.split("?")[0]
	rurl=url[::-1]
	if len(rurl)<=4:
		return False
	rurl = rurl.split("://")[-1]
	htmls=["html","htm","php","/","jsp"]
	for html in htmls:
		if rurl.find(html[::-1])==0:
			return True 
	return False
	return len(rurl.split("/"))==1
	return False

def is_html(ct_type):
	page_types=["text/html"]
	for pg_type in page_types:
		if ct_type.find(pg_type)>=0:
			return True 
	return False

def html2urls(contents,base_url):
	import bs4
	soup=bs4.BeautifulSoup(contents,"html5lib")
	lnks=[ i for i in soup.descendants if type(i) == bs4.element.Tag and (i.has_attr('src') or i.has_attr('href'))]
	olnks=[ i.attrs['src'] for i in lnks if i.has_attr('src')] + [ i.attrs['href'] for i in lnks if i.has_attr('href')]
	lnks=[i.lower() for i in olnks]
	outs = fullurls(lnks,base_url)
	return outs

def html2lnks(contents,base_url):
	import bs4
	soup=bs4.BeautifulSoup(contents,"html5lib")
	lnks=[ i for i in soup.descendants if type(i) == bs4.element.Tag and (i.has_attr('src') or i.has_attr('href'))]
	olnks=[ (i.attrs['src'],i.text,i) for i in lnks if i.has_attr('src')] + [ (i.attrs['href'],i.text,i) for i in lnks if i.has_attr('href')]
	outs=[]
	for lnk in lnks:
		url=fullurl(lnk[0],base_url)
		if url == None:
			continue 
		outs.append([url,lnk[1],lnk[2]])
	return outs

	
def host(url,nodes=-1):
	url=url.split("?")[0]
	url = url.split("://")[-1]
	url = url.split("/")[0]
	if nodes < 0:
		return url 
	urls = url.split(".")[:nodes]
	return ".".join(urls)
	
def http_base(url):
	hst = host(url)
	url=url.split("?")[0]
	splts = url.split("://")
	if len(splts)>1:
		pfx = splts[0]+"://"
	else:
		pfx = ""
	return pfx + hst

deal_url = {}
def fullurl(url,base):
	global deal_url
	backurl = url 
	backbase = base
	outs=[]
	prefix=base.split("://")[0]
	base_url=base.split("?")[0]
	last_url=base_url.split("/")[-1]
	base_path=base_url[:len(base_url)-len(last_url)]
	if base_path == "":
		base_path = base_url+"/"
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
	url=reduce_url(url)
	deal_url[url]=(backurl,backbase)
	return url

def fullurls(urls,base):
	outs=[]
	prefix=base.split("://")[0]
	base_url=base.split("?")[0]
	last_url=base_url.split("/")[-1]
	base_path=base_url[:len(base_url)-len(last_url)]
	if base_path == "":
		base_path = base_url+"/"
	base_url=host(base_url)
	for url in urls:
		if nourl(url):
			continue 
		elif url.find('://')>=0:
			pass
		elif url[:2]=="//":
			url=prefix+":"+url 
		elif url[0]=='/':
			url=prefix+"://"+base_url+url 
		else:
			url=base_path+url 
		url=reduce_url(url)
		outs.append(url)
	return outs

def header( refer = None):
	user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' 
	user_agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36';
	headers = { 'User-Agent' : user_agent }
	if refer is not None:
		headers['Refere'] = refer
	return headers

user_agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36';


def reduce_url(url):
	urls = url.split("?")
	url = urls[0]
	parm = ""
	if len(urls)>1:
		parm = "?".join(urls[1:])
		parm = "?"+parm 
	cnt=url.count("..")
	if cnt==0:
		return "".join(url.split("/."))+parm 
	turls  =url.split("://")
	pfx = ""
	if len(turls)==1:
		pfx = turls[0] + "://"
		url = turls[1]
	urls = url.split("/")
	i = 0
	l = len(urls)
	outs = []
	while i < l:
		node = urls[i]
		if node == '..':
			i+=1
			outs = outs[:-1]
		else:
			outs.append(node)
		i+=1
	url = pfx + "/".join(outs)
	return "".join(url.split("/."))+parm 
	
def page_name(url):
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

def nourl(url):
	url=url.split("?")[0]
	#pattern="([^a-zA-Z0-9\./:_#]*)"
	#still something no incluede, so ...
	#rst=re.findall(pattern,url)
	#for i in rst:
	#	if i!='':
	#		return True
	#tmp=url.split('.')
	#if len(tmp)<=1:
	#	return True
	js='javascript'
	if len(url)==0 or url[:len(js)]==js or url[0] in ['#','"',"'"]:
		return True 
	return False


# fetch links from html context by re.findall 
# and deal links
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
	import re
	urls=re.findall(pattern,cts)
	outs=[]
	for url in urls:
		outs.append(url[2]+url[3])
	return outs 

pattern="(href|src)=('([^']*)'|\"([^\"]*)\")"
