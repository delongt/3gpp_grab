# -*- coding: utf-8 -*-
'''
Created on 2020-07-14
@author: delong tang
'''

import re
import os

import Comm as C

path_root = './'
path_rfc = './rfc'


def clean_rfc(l):
	try:
		d = {}
		for ll in l:
			if 'rfc' not in ll:
				continue
			r = re.findall('\d+', ll)
			if (1 == len(r)):
				i = int(r[0])
				if i not in d:
					d[i] = os.path.join(path_rfc, ll)
				elif 'txt' in ll:
					d[i] = os.path.join(path_rfc, ll)
		return d
	except Exception as ex:
		C.printEx(ex)
	return {}

def rfc_start(l):
	try:
		r = re.match('\d+', l)
		if r is None:
			return 0
		return 1
	except Exception as ex:
		C.printEx(ex)
	return 0

def rfc_end(l):
	try:
		r0 = re.search('(DOI: \d+.\d+/RFC\d+)', l)
		r1 = re.search('Not Issued', l)
		if (r0 is None) and (r1 is None):
			return 0
		else:
			return 1 
	except Exception as ex:
		C.printEx(ex)
	return 1

def rfc_record(l):
	try:
		r = re.findall('\([^\)]+\)', l)
		if r is None:
			return ''
		s = l
		for e in r:
			if (('Format' in e) or ('DOI' in e)):
				s = s.replace(e, '')
		return s.strip()
	except Exception as ex:
		C.printEx(ex)
	return ''

_str_href = '''<a href="{href_}">{name_}</a>'''
def int_html(s, d):
	try:
		i = int(s)
		if i not in d:
			return ''
		r = _str_href.format(href_ = d[i], name_ = s)
		return r
	except Exception as ex:
		C.printEx(ex)
	return ''

def str_html(l, d):
	try:
		r = re.match('\d+', l)
		if r is None:
			return 0, ''
		i= int(r[0])
		ss = int_html(r[0], d)
		if (0 <len(ss)):
			s = l.replace(r[0], ss)
		else:
			s = l
		r = re.findall('RFC\d+', s)
		if r is not None:
			for rr in r:
				ss = int_html(rr[3:], d)
				if (0 <len(ss)):
					s = s.replace(rr[3:], ss)
		return i, s
	except Exception as ex:
		C.printEx(ex)
	return 0, ''

_str_html = '''<html>
 <head>
  <title>RFC (powered by delong tang)</title>
 </head>
 <body link="blue" vlink="purple">
  <table border="0">
   <col>
   {content_} 
  </table>
 </body>
</html>'''

_str_table = '''   <tr>
    <td>{series_}</td>
   </tr>'''
def format_idx_html(m, d):
	try:
		r = {}
		for l in m:
			ri,rs = str_html(l, d)
			if (0 != ri):
				r[ri] = rs
		s = ''
		for i in range(20000):
			if i in r:
				ss = _str_table.format(series_ = r[i])
				s = s + '\r\n' + ss
		ss = _str_html.format(content_ = s)
		return ss
	except Exception as ex:
		C.printEx(ex)
	return {}

def format_idx_file():
	try:
		p = os.path.join(path_rfc, 'rfc-index.txt')
		f = open(p, 'r')
		l = f.readlines()
		f.close()
		r = []
		rr = ''
		ir = 0
		for i in range(len(l)):
			try:
				if (0 == ir):
					rsr = rfc_start(l[i])
					if (1 == rsr):
						rr = l[i].strip()
						ir = 1
				elif (1 == ir):
					rr = rr + ' ' + l[i].strip()
					rer = rfc_end(rr)
					if (1 == rer):
						ir = 0
						rs = rfc_record(rr)
						r.append(rs)
			except Exception as ex:
				C.printEx(ex)
				continue
		return r
	except Exception as ex:
		C.printEx(ex)
	return []

def scan_rfc():
	try:
		if not os.path.exists(path_rfc):
			return
		if not os.path.isdir(path_rfc):
			return
		l = os.listdir(path_rfc)
		if (1 > len(l)):
			return
		d = clean_rfc(l)
		if (1 > len(d)):
			return
		m = format_idx_file()
		if (1 > len(m)):
			return
		s = format_idx_html(m, d)
		if (1 > len(s)):
			return
	except Exception as ex:
		C.printEx(ex)
		return
	try:
		s = s.encode('utf-8')
		p = os.path.join(path_root, 'RFC_SPEC.html')
		f = open(p, mode = 'wb')
		f.write(s)
		f.close()
	except Exception as ex:
		C.printEx(ex)
		return
	return

if __name__ == '__main__':
    try:
        scan_rfc()
    except Exception as ex:
        C.printEx(ex)
    pass

