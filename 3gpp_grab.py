# -*- coding: utf-8 -*-
'''
Created on 2020-07-14
@author: delong tang
'''

import os
import re
import httplib2
from bs4 import BeautifulSoup
import zipfile

http2handle = httplib2.Http()

path_spec = '/home/share/3gpp/specs/'
url_spec = 'https://www.3gpp.org/ftp/Specs/archive' 
url_spec_rm = 'https://www.3gpp.org/DynaReport/SpecReleaseMatrix.htm'
spec_list = ['21', '22', '23', '24', '28', '29', '32', '33', '35', '36', '37', '38']

path_contrib = '/home/share/3gpp/contribs/'
contrb_list = [ \
                ['TSGR', 'https://www.3gpp.org/ftp/tsg_ran/TSG_RAN', 85], \
                ['TSGR1', 'https://www.3gpp.org/ftp/tsg_ran/WG1_RL1', 100],\
                ['TSGR2', 'https://www.3gpp.org/ftp/tsg_ran/WG2_RL2', 106],\
                ['TSGR3', 'https://www.3gpp.org/ftp/tsg_ran/WG3_Iu', 102],\
                ['TSGR4', 'https://www.3gpp.org/ftp/tsg_ran/WG4_Radio', 93],\
                ['TSGS', 'https://www.3gpp.org/ftp/tsg_sa/TSG_SA', 85],\
                ['TSGS1', 'https://www.3gpp.org/ftp/tsg_sa/WG1_Serv', 85],\
                ['TSGS2', 'https://www.3gpp.org/ftp/tsg_sa/WG2_Arch', 133],\
                ['TSGS3', 'https://www.3gpp.org/ftp/tsg_sa/WG3_Security', 95],\
                ['TSGS5', 'https://www.3gpp.org/ftp/tsg_sa/WG5_TM', 127],\
                ['TSGS6', 'https://www.3gpp.org/ftp/tsg_sa/WG6_MissionCritical', 34]\
              ]

def printex(s):
    print(s)
    return

def get_href(s):
    try:
        r1 = re.findall('href=".*"',str(s))
        r2 = re.findall('>.*<',str(s))
        if ((1 == len(r1)) or (1 == len(r2))):
            return r2[0][1:-1], r1[0][6:-1]
    except Exception as ex:
        printex(str(ex))
    return '',''

def get_plain_text(s):
    try:
        ss = str(s)
        while(1):
            r1 = re.findall('<[^>]*>',ss)
            if 0 < len(r1):
                for e in r1:
                    ss = ss.replace(e, '')
            else:
                break
        return ss
    except Exception as ex:
        printex(str(ex))
    return ''
    
def get_spec_name(s):
    try:
        ls = s.find_all(name='td');
        if (2 > len(ls)):
            return '',''
        s1 = get_plain_text(ls[0])
        s1 = s1.strip()
        s2 = get_plain_text(ls[1])
        s2 = s2.strip()
        if ((0 <len(s1)) and (0 <len(s2))):
            return s1, s2 
    except Exception as ex:
        printex(str(ex))
    return '',''

def parse_matrix(c, cs):
    try:
        soup = BeautifulSoup(c, "html5lib")
        soup.prettify()
        l = []
        ll = soup.find_all(name='tr')
        if (1 > len(ll)):
            return []
        for e in ll:
            l1, l2 = get_spec_name(e)
            if (0 < len(l1)):
                l.append([l1, l2])
        return l
    except Exception as ex:
        printex(str(ex))
    return []

def check_resp(r):
    try:
        if ('OK' not in r.reason):
            return False, ''  
        s = r['content-type']
        if ('text/html' not in s):
            return False, ''
        l = s.split(';')
        for e in l:
            if 'charset=' in e:
                ll = e.split('charset=')
                if (2 == len(ll)):
                    return True, ll[1]
    except Exception as ex:
        printex(str(ex))
    return False, ''

def get_spec_title(s, l):
    try:
        ll = []
        for l1, l2 in l:
            if l1 in s:
                ll.append([l1,l2])
        if (1 > len(ll)):
            return ''
        if (1 < len(ll)):
            ll = sorted(ll, key=lambda k: k[0], reverse = True)
        if 'withdrawn' not in ll[0][1]:
            return ll[0][1]
    except Exception as ex:
        printex(str(ex))
    return ''

def get_zip_file(f,h):
    try:
        r,c = http2handle.request(h)
    except Exception as ex:
        printex(str(ex))
        return False
    try:
        if ('OK' not in r.reason):
            return False  
        s = r['content-type']
        if ('zip' in s):
            with open(f, 'wb')as fp:
                fp.write(c)
            print('get ' + h)
            return True
    except Exception as ex:
        printex(str(ex))
    return False

def parse_url(c, s):
    try:
        soup = BeautifulSoup(c, "html5lib")
        soup.prettify()
        l = []
        ll = soup.find_all(name='a')
        if (1 > len(ll)):
            return []
        for e in ll:
            l1, l2 = get_href(e)
            if (0 < len(l1)):
                l.append([l1, l2])
        return l
    except Exception as ex:
        printex(str(ex))
    return []

def get_spec_file(p, n, h):
    try:
        r,c = http2handle.request(h)
        print('get ' + h)
    except Exception as ex:
        printex(str(ex))
        return ''
    try:
        b, cs = check_resp(r);
        if (not b):
            return ''
    except Exception as ex:
        printex(str(ex))
        return ''
    try:
        l = parse_url(c, cs)
        if (1 > len(l)):
            return ''
    except Exception as ex:
        printex(str(ex))
        return ''
    try:
        ll = []
        for l1, l2 in l:
            if ((h in l2) and ('zip' in l2)):
                ll.append([l1, l2])
        ll = sorted(ll, key=lambda k: k[0], reverse = True)
        f = os.path.join(p, ll[0][0])
        if (os.path.exists(f)):
            return f
        if get_zip_file(f,ll[0][1]):
            return f
    except Exception as ex:
        printex(str(ex))
    return ''

def get_series(s, p, lm):
    ls = []
    try:
        r,c = http2handle.request(s)
        print('get ' + s)
    except Exception as ex:
        printex(str(ex))
        return []
    try:
        b, cs = check_resp(r);
        if (not b):
            return []
    except Exception as ex:
        printex(str(ex))
        return []
    try:
        l = parse_url(c, cs)
        if (1 > len(l)):
            return []
    except Exception as ex:
        printex(str(ex))
        return []
    try:
        for l1,l2 in l:
            if s not in l2:
                continue
            sn = get_spec_title(l1, lm)
            if 1 > len(sn):
                continue
            fp = get_spec_file(p, l1, l2) 
            if 0 < len(fp):
                ls.append([l1,sn,fp])
        return ls
    except Exception as ex:
        printex(str(ex))
    return []

def parse_specs(r, c):
    return

def grab_spec():
    try:
        r,c = http2handle.request(url_spec_rm)
        print('get ' + url_spec_rm)
    except Exception as ex:
        printex(str(ex))
        return {}
    try:
        b, cs = check_resp(r);
        if (not b):
            return {}
    except Exception as ex:
        printex(str(ex))
        return {}
    try:
        lm = parse_matrix(c, cs)
        if (1 > len(lm)):
            return {}
    except Exception as ex:
        printex(str(ex))
        return {}
    try:
        r,c = http2handle.request(url_spec)
        print('get ' + url_spec)
    except Exception as ex:
        printex(str(ex))
        return {}
    try:
        b, cs = check_resp(r);
        if (not b):
            return {}
    except Exception as ex:
        printex(str(ex))
        return {}
    try:
        l = parse_url(c, cs)
        if (1 > len(l)):
            return  {}
    except Exception as ex:
        printex(str(ex))
        return {}
    try:
        d = {}
        for l1,l2 in l:
            if '_series' not in l1:
                continue
            for e in spec_list:
                if e in l1:
                    p = os.path.join(path_spec, l1)
                    if (not os.path.exists(p)):
                        os.mkdir(p)
                    print('begin to get ' + l1)
                    d[e] = get_series(l2, p, lm)
                    print('end to get ' + l1)
        return d
    except Exception as ex:
        printex(str(ex))
    return {}

str_html = '''<html>
 <head>
  {title_}
 </head>
 <body link="blue" vlink="purple">
  <table width="800" border="1">
   <col width="50">
   <col width="150">
   <col width="680">
   {content_} 
  </table>
 </body>
</html>'''

str_table = '''   <tr>
    <td colspan="3">{series_}</td>
   </tr>'''

str_tr0 = '''   <tr>
    <td rowspan="{count_}"></td>
    <td><a href="{href_}">{name_}</a></td>
    <td>{title_}</td>
   </tr>'''

str_tr1 = '''   <tr>
    <td><a href="{href_}">{name_}</a></td>
    <td>{title_}</td>
   </tr>'''

def html_spec(d):
    try:
        s0 = ''
        for e in d:
            l = d[e] 
            icnt = len(l)
            if (1 > icnt):
                continue
            s1 = ''
            for n, t, p in l:
                if (0 == len(s1)):
                    s1 = str_tr0.format(count_ = str(icnt), href_ = p, name_ = n, title_ = t)
                    s1 = s1 + '\n'
                else:
                    s1 = s1 + str_tr1.format(href_ = p, name_ = n, title_ = t)
                    s1 = s1 + '\n'
            s0 = s0 + str_table.format(series_ = e)
            s0 = s0 + '\n' + s1
        if (1 > len(s0)):
            return
    except Exception as ex:
        printex(str(ex))
        return
    try:
        s = str_html.format(title_ = '3GPP TS & TR', content_ = s0)
        p = os.path.join(path_spec, '3gpp_spec.html')
        with open(p, 'w')as fp:
            fp.write(s)
    except Exception as ex:
        printex(str(ex))
    return

def check_meeting_num(t, n):
    try:
        l = t.split('_') 
        if (2 < len(l)):
            return False
        i = re.search("\d+",l[1]).group(0)
        i = int(i)
        if (i >= n):
            return True 
    except Exception as ex:
        printex(str(ex))
    return False

def get_zip_fn(f):
    try:
        z = zipfile.ZipFile(f)
        l = z.namelist()
        j = len(l)
        if (1 > j):
            return ''
        elif (1 == j):
            return l[0]
        else:
            s = l[0]
            for i in range(1, j):
                s = s + '\n' + l[i]
            return s     
    except Exception as ex:
        printex(str(ex))
    return ''

def grab_meeting_file(p, h):
    try:
        r,c = http2handle.request(h)
        print('get ' + h)
    except Exception as ex:
        printex(str(ex))
        return []
    try:
        b, cs = check_resp(r);
        if (not b):
            return []
    except Exception as ex:
        printex(str(ex))
        return []
    try:
        l = parse_url(c, cs)
        if (1 > len(l)):
            return []
    except Exception as ex:
        printex(str(ex))
        return []
    ll = []
    for l1, l2 in l:
        try:
            if (not ((h in l2) and ('zip' in l2))):
                continue
            f = os.path.join(p, l1)
            if not (os.path.exists(f)):
                if not get_zip_file(f,l2):
                    print('cannot get ' + l2)
                    continue
            s = get_zip_fn(f)
            if (0 < len(s)):
                ll.append([l1, s, f])
        except Exception as ex:
            printex(str(ex))
    return ll

def grab_meeting(p, t, h, n):
    try:
        if not check_meeting_num(t, n):
            return []
        pp = os.path.join(p, t)
        if not (os.path.exists(pp)):
            os.mkdir(pp)
    except Exception as ex:
        printex(str(ex))
        return []
    try:
        r,c = http2handle.request(h)
        print('get ' + h)
    except Exception as ex:
        printex(str(ex))
        return []
    try:
        b, cs = check_resp(r);
        if (not b):
            return []
    except Exception as ex:
        printex(str(ex))
        return []
    try:
        l = parse_url(c, cs)
        if (1 > len(l)):
            return []
    except Exception as ex:
        printex(str(ex))
        return []
    try:
        for ht, hh in l:
            if (('Docs' in ht) and ('Docs' in hh)):
                return grab_meeting_file(pp, hh)
    except Exception as ex:
        printex(str(ex))
    return []

def grab_contrib(t, h, n):
    try:
        p = os.path.join(path_contrib, t)
        if not os.path.exists(p):
            os.mkdir(p)
    except Exception as ex:
        printex(str(ex))
        return {}
    try:
        r,c = http2handle.request(h)
        print('get ' + h)
    except Exception as ex:
        printex(str(ex))
        return {}
    try:
        b, cs = check_resp(r);
        if (not b):
            return {}
    except Exception as ex:
        printex(str(ex))
        return {}
    try:
        l = parse_url(c, cs)
        if (1 > len(l)):
            return  {}
    except Exception as ex:
        printex(str(ex))
        return {}
    try:
        d = {}
        for mt, mh in l:
            if ((t in mt) and (h in mh)):
                print('begin to get ' + mh)
                ll = grab_meeting(p, mt, mh, n)
                print('end to get ' + mh)
                if (0 < len(ll)):
                    d[mt] = ll
        if (0 < len(d)):
            return d
    except Exception as ex:
        printex(str(ex))
        return {}
    return {}

def html_contrib(t, d):
    try:
        s0 = ''
        for e in d:
            l = d[e] 
            icnt = len(l)
            if (1 > icnt):
                continue
            s1 = ''
            for ln, lt, lp in l:
                if (0 == len(s1)):
                    s1 = str_tr0.format(count_ = str(icnt), href_ = lp, name_ = ln, title_ = lt)
                    s1 = s1 + '\n'
                else:
                    s1 = s1 + str_tr1.format(href_ = lp, name_ = ln, title_ = lt)
                    s1 = s1 + '\n'
            s0 = s0 + str_table.format(series_ = e)
            s0 = s0 + '\n' + s1
        if (1 > len(s0)):
            return
    except Exception as ex:
        printex(str(ex))
        return
    try:
        s = str_html.format(title_ = t, content_ = s0)
        p = os.path.join(path_contrib, t + '.html')
        with open(p, 'w')as fp:
            fp.write(s)
    except Exception as ex:
        printex(str(ex))
    return

if __name__ == '__main__':
    try:
        d = grab_spec()
        if (0 < len(d)):
            html_spec(d)
    except Exception as ex:
        printex(str(ex))
    try:
        for t, h, n in contrb_list:
            print('begin to get ' + h)
            d = grab_contrib(t, h, n)
            print('end to get ' + h)
            if (0 < len(d)):
                html_contrib(t, d)
    except Exception as ex:
        printex(str(ex))
    exit(0)
