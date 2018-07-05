# coding=utf-8
Contents = ""
def show(keys):
	for k in keys:
		print k[0],k[1]
def remove(keys,*names):
	for name in names:
		objs = [k for k in keys if k[0] == name]
		if len(objs)==0:
			continue 
		keys.remove(objs[0])
	show(keys)
# get words of n&v cut from jieba 
def pcut(contents):
	global Contents
	Contents=contents
	import jieba.posseg 
	outs=jieba.posseg.cut(contents)
	arr=[]
	for word,flag in outs:
		if flag[0] in ["n","v"]:
			arr.append(word)
	return arr 

# get words cut from jieba 
def cut(contents):
	outs=jieba.cut(contents)
	arr=[]
	for i in outs:
		arr.append(i)
		print i;
	return arr 

# jieba.analyse.extract_tags(sentence, topK=20, withWeight=False, allowPOS=())

# get list of words from tf-idf
def tf_idf(contents, count = 10):
	import jieba.analyse
	outs=jieba.analyse.extract_tags(contents, topK = count, withWeight=True)
	arr=[]
	for item in outs:
		arr.append(item[0])
	return arr
# get list of [words,weight] from tf-idf
def tf_idfs(contents, count = 10):
	import jieba.analyse
	outs=jieba.analyse.extract_tags(contents, topK = count, withWeight=True)#, allowPOS=('n','nr','ns','eng','v'))
	arr=[]
	for item in outs:
		arr.append([item[0],item[1]])
	return arr

# jieba.analyse.extract_tags(sentence, topK=20, withWeight=True, allowPOS=('n','nr','ns'))

def html2words(content, count = 10):
	content=contents(content)
	return tf_idfs(content,count)

# left vector of rst from tf-idf normalized to 1.0
def normal(keys):
	rst = 0.0
	for obj in keys:
		rst+=obj[1]
	if rst>0:
		rst = 1.0/rst 
	for obj in keys:
		obj[1]*=rst 
	return keys

# cos used for words from tf-idfs
def cos(a,b):
	rst=0.0
	for obja in a:
		for objb in b:
			if obja[0]==objb[0]:
				rst+=obja[1]*objb[1]
	dsta=0.0
	for obja in a:
		dsta+=obja[1]**2
	dstb=0.0
	for objb in b:
		dstb+=objb[1]**2
	dst=(dsta*dstb)**0.5
	if dst == 0.0:
		return 0.0
	return rst/dst
	
# simple demo for set similar
def similar(a,b):
	return 1.0*len(a.intersection(b))/len(a.union(b))

def text_rand(contents, count = 10):
	import jieba.analyse
	outs = jieba.analyse.textrank(contents, topK = count, withWeight=True,allowPOS=('n','nr','ns','eng'))
	arr=[]
	for item in outs:
		#print item[0],item[1]
		arr.append([item[0],item[1]])
	return arr

# get string from obj that has contents
# find this work no good, replace it already(see below function)
def contents(html):
	import bs4
	soup=bs4.BeautifulSoup(html,"html5lib")
	results=[]
	past=[]
	for i in soup.descendants:
		if i.name=="script" or i.name==None or i.string==None:
			past.append(i)
			continue 
		results.append(i.string)
	return results,past

# get string from obj that has contents
def contents(soup):
	import bs4
	if type(soup) in [str,unicode]:
		soup=bs4.BeautifulSoup(soup,"html5lib")
	rst=[]
	#print "soup:",type(soup)
	#print "soup.contents:",soup.contents
	for child in soup.contents:
		if child.name in ["script","style"]  or type(child) in [bs4.element.Comment,bs4.element.Doctype]:
			continue 
		if child.string == None:
			rst+=contents(child)
		else:
			rst.append(child.string)
	return ''.join(rst)
