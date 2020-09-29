# -*- coding: utf-8 -*-
'''
Created on 2020-07-14
@author: delong tang
'''

import time
import re
import httplib2
import bs4
from bs4 import BeautifulSoup as BS

#import pickle  

hh = httplib2.Http()
hhs = httplib2.Http(disable_ssl_certificate_validation=True)

def strT():
    s = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    s = s + ' -- '
    return s 

def printInfo(s):
    print(strT() + s)
    return

def printEx(s):
    printInfo('Except : ' + str(s))
    return

def getLabal(s, l):
    ll = []
    try:
        if (isinstance(s, str) or isinstance(s, bytes)):
            soup = BS(s, "html5lib")
            soup.prettify()
            ll = soup.find_all(name=l)
        elif isinstance(s, bs4.element.Tag):
            ll = s.find_all(name=l)
    except Exception as ex:
        printEx(ex)
    return ll

def getText(s):
    try:
        if isinstance(s, bs4.element.Tag):
            ss = str(s)
        else:
            ss = s
        while(1):
            r1 = re.findall('<[^>]*>',ss)
            if 0 < len(r1):
                for e in r1:
                    ss = ss.replace(e, '')
            else:
                break
        return ss.strip()
    except Exception as ex:
        printEx(ex)
    return ''

def getHttp(url, sorno = 'http'):
    try:
        if ('http' == sorno):
            r,c = hhs.request(url)
        elif ('https' == sorno):
            r,c = hh.request(url)
        else:
            return 'err', None, 'err'
        printInfo('get ' + url)
    except Exception as ex:
        printEx(ex)
        return 'err', None, 'err'
    rt = 'err'
    ct = 'err'
    try:
        if ('OK' not in r.reason):
            return 'err', None, 'err'  
        s = r['content-type']
        if ('text/html' in s):
            rt = 'html'
            l = s.split(';')
            for e in l:
                if 'charset=' in e:
                    ll = e.split('charset=')
                    if (2 == len(ll)):
                        ct = ll[1]
        elif ('zip' in s):
            rt = 'zip'
            ct = 'zip'
        elif ('officedocument' in s):
            rt = 'xls'
            ct = 'xls'
        elif ('pdf' in s):
            rt = 'pdf'
            ct = 'pdf'
    except Exception as ex:
        printEx(ex)
        return 'err', None, 'err'
    return rt, c, ct

def getHref(s):
    try:
        if isinstance(s, bs4.element.Tag):
            ss = str(s)
        else:
            ss = s
        h = re.findall('href="[^"]*"', ss)
        if ((0 < len(h)) and (7 < len(h[0]))):
            hh = h[0][6:-1]
            return hh
    except Exception as ex:
        printEx(ex)
    return ''









