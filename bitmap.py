#coding=utf-8

class bitarr(object):
	def __init__(self, size=128):
		self.size = size
		size >>= 3
		self.bits = bytearray(size)
	def cut(self, pos):
		return pos % self.size
	def __setitem__(self, pos, val):
		byte_index = pos >> 3
		bit_index = (pos & 7)
		tmp = 1 << bit_index
		if val == 1:
			self.bits[byte_index] |= tmp
		elif val == 0:
			self.bits[byte_index] &= 255 - tmp
		else:
			raise Exception("val not in (0,1): "+str(val))
	def __getitem__(self, pos):
		byte_index = pos >> 3
		bit_index = (pos & 7)
		v = (self.bits[byte_index] & (1<<bit_index))>>bit_index
		return v
	def __str__(self):
		s = ""
		for c in self.bits[::-1]:
			t = bin(c)[2:]
			t = "%8s"%(t,)
			s += t.replace(' ','0')
		return s

class bitmap(bitarr):
	def __init__(self, size, *funcs):
		super(bitmap,self).__init__(size)
		self.funcs = [bitfc(size, fc) for fc in funcs]
	def update(self, s):
		for fc in self.funcs:
			pos = fc(s)
			self[pos] = 1

def log2i(size):
	cnt = 0
	while size > 1:
		size >>= 1
		cnt += 1
	return cnt

class bitfc(object):
	def __init__(self, size, hashfc = None):
		self.hash = hashfc
		self.size = size
		self.count = log2i(size)
	def __call__(self, s):
		if self.hash is None or type(s) not in (str,unicode):
			return fc(self.size,s)
		s = self.hash(s)
		index = s2pos(s, self.count)
		return index % self.size

def s2pos(hexs, size):
	size >>= 2
	size += 1
	s = hexs[-size:]
	bytes = bytearray(s)
	rst = 0
	for c in bytes:
		if c < 97:
			i = c - 48
		else:
			i = c - 97 + 10
		rst = (rst << 4) + i
	return rst

def hashfc(fc):
	def outf(s):
		tf = fc()
		tf.update(s)
		return tf.hexdigest()
	return outf

import hashlib
sha1 = hashfc(hashlib.sha1)
md5 = hashfc(hashlib.md5)

bm=bitmap(256,md5,sha1)
for i in xrange(512/4):
	bm.update(str(i))

str(bm)
