# -*- coding: utf-8 -*-
'''
Created on 2020-07-14
@author: delong tang
'''

import os
import re

import Comm as C

path_root = './'

path_spec = os.path.join(path_root, 'itut')

url_spec_ref = 'https://www.itu.int/en/ITU-T/publications/Pages/recs.aspx'
url_spec_uri = 'https://www.itu.int/rec/T-REC-'
    




def get_file_name(c, e):
    l = []
    s = ''
    try:
        l0 = C.getLabal(c, 'tr')
        if (1 > len(l0)):
            return []
        for l1 in l0:
            l2 = C.getLabal(l1, 'td')
            if (3 != len(l2)):
                continue
            l3 = str(l2[2])
            if ('In force' not in l3):
                continue
            l4 = str(l2[0])
            r = re.findall(';parent=[^"]+"', l4)
            if (1 != len(r)):
                continue
            if (e in r[0]):
                s = r[0][8:-1]
                n = C.getText(l2[1])
                l.append([s, n])
    except Exception as ex:
        C.printEx(ex)
        return l
    return l

def get_pdf_url(s):
    try:
        h = url_spec_uri + s[6:] + '/e'
        rt, c, ct = C.getHttp(h)
        if ('html' not in rt):
            return '', ''
    except Exception as ex:
        C.printEx(ex)
        return '', ''
    try:
        d = {0:'',1:''}
        lan = ''
        l0 = C.getLabal(c, 'tr')
        if (1 > len(l0)):
            return ''
        for l1 in l0:
            l2 = C.getLabal(l1, 'td')
            if (5 != len(l2)):
                continue
            s1 = str(l2[0])
            s2 = C.getText(s1)
            s2 = s2.strip() 
            if (0 < len(s2)):
                lan = s2
            s3 = str(l2[1])
            s4 = C.getText(s3)
            h = C.getHref(s3)
            if (s not in h):
                continue
            if ('PDF' in s4):
                if ('English' in lan):
                    d[1] = h
                elif ('Chinese' in lan):
                    d[0] = h
        if (0 < len(d[0])):
            return d[0]
        elif (0 < len(d[1])):
            return d[1]
        else:
            return ''
    except Exception as ex:
        C.printEx(ex)
        return ''
    return s

def get_pdf_file(s, t):
    try:
        p = os.path.join(path_spec, t + '.pdf')
        if os.path.exists(p):
            return p
        if ('&amp;' in s):
            s = s.replace('&amp;', '&')
        rt, c, ct = C.getHttp(s)
        if ('pdf' not in rt):
            return ''
    except Exception as ex:
        C.printEx(ex)
        return False
    try:
        f = open(p, 'wb')
        f.write(c)
        f.close()
        C.printInfo('write ' + p)
        return p
    except Exception as ex:
        C.printEx(ex)
    return ''

'''
https://www.itu.int/rec/T-REC-A.1/en
https://www.itu.int/rec/T-REC-A.1-201909-I/en
'''
def grab_file(e):
    try:
        h = url_spec_uri + e + '/e'
        rt, c, ct = C.getHttp(h)
        if ('html' not in rt):
            return []
    except Exception as ex:
        C.printEx(ex)
        return []
    try:
        l = get_file_name(c, e)
        if (1 > len(l)):
            return []
    except Exception as ex:
        C.printEx(ex)
        return []
    r = []
    for s, n in l:
        try:
            u = get_pdf_url(s)
            if e not in u:
                continue
        except Exception as ex:
            C.printEx(ex)
            return []
        try:
            f = get_pdf_file(u, s)
            if e not in s:
                continue
            r.append([s, n, f])
        except Exception as ex:
            C.printEx(ex)
            continue
    return r

def get_files_href(c):
    try:
        l = C.getLabal(c, 'td')
        if (2 != len(l)):
            return '', ''
        s = C.getText(l[0])
        h = C.getHref(l[0])
        if ('./recommendation.asp?lang=en&amp;parent=T-REC-' not in h):
            return '', ''
        t = C.getText(l[1])
        return s, t
    except Exception as ex:
        C.printEx(ex)
    return '', ''

def parse_files(c, u):
    r = {}
    try:
        l = C.getLabal(c, 'tr')
        if (1 > len(l)):
            return {}
        for e in l:
            s, t = get_files_href(e)
            if ((0 < len(s)) and ('[Withdrawn]' not in t)):
                r[s] = t
    except Exception as ex:
        C.printEx(ex)
    return r

def grab_series(u):
    try:
        h = url_spec_uri + u + '/e'
        rt, c, ct = C.getHttp(h)
        if ('html' not in rt):
            return {}
    except Exception as ex:
        C.printEx(ex)
        return {}
    try:
        d = parse_files(c, u)
    except Exception as ex:
        C.printEx(ex)
    return d

def get_ref_info(e):
    try:
        ss = str(e)
        if 'title=' not in ss:
            return '', ''
        if 'href=' not in ss:
            return '', ''
        if '/itu-t/recommendations/index.aspx?ser=' not in ss:
            return '', ''
        s = C.getText(ss)
        if (not (1 == len(s))):
            return '', ''
        tt = re.findall('title="[^"]*"', ss)
        if ((0 < len(tt)) and (8 < len(tt[0]))):
            t = tt[0][7:-1]
        else:
            return '', ''
        return s, t
    except Exception as ex:
        C.printEx(ex)
    return '', ''

def parse_series_info(c):
    r = {}
    try:
        l = C.getLabal(c, 'a')
        if (1 > len(l)):
            return {}
        for e in l:
            s, t = get_ref_info(e)
            if (1 == len(s)):
                r[s] = t
    except Exception as ex:
        C.printEx(ex)
    return r

def grab_series_info():
    try:
        rt, c, ct = C.getHttp(url_spec_ref)
        if ('html' not in rt):
            return {}
    except Exception as ex:
        C.printEx(ex)
        return {}
    try:
        d = parse_series_info(c)
    except Exception as ex:
        C.printEx(ex)
    return d

str_html = '''<html>
 <head>
  ITU-T
 </head>
 <body link="blue" vlink="purple">
  <table border="0">
   <col width="80">
   <col width="150">
   <col>
   {content_} 
  </table>
 </body>
</html>'''

str_table = '''   <tr>
    <td>{series_}</td>
    <td colspan="3">{title_}</td>
   </tr>'''

str_tr0 = '''   <tr>
    <td></td>
    <td><a href="{href_}">{name_}</a></td>
    <td colspan="2">{title_}</td>
   </tr>'''

str_tr1 = '''   <tr>
    <td></td>
    <td></td>
    <td><a href="{href_}">{name_}</a></td>
    <td>{title_}</td>
   </tr>'''

def html_itut(d):
    s = ''
    try:
        for e in d:
            for ee in d[e][1]:
                if (1 == len(d[e][1][ee])):
                    ss = str_tr0.format(href_ = d[e][1][ee][0][2], name_ = d[e][1][ee][0][0], title_ = d[e][1][ee][0][1])
                    s = s + ss;
                else:
                    ss = str_tr0.format(href_ = d[e][1][ee][0][2], name_ = d[e][1][ee][0][0], title_ = d[e][1][ee][0][1])
                    s = s + ss;
                    for i in range(1, len(d[e][1][ee])):
                        ss = str_tr1.format(href_ = d[e][1][ee][i][2], name_ = d[e][1][ee][i][0], title_ = d[e][1][ee][i][1])
                        s = s + ss;
            ss = str_table.format(series_ = e, title_ = d[e][0])
            s = ss + s
        ss = str_html.format(content_ = s)
    except Exception as ex:
        C.printEx(ex)
        return
    try:
        s = s.encode('utf-8')
        p = os.path.join(path_root, 'ITUT_SPEC.html')
        f = open(p, mode = 'wb')
        f.write(s)
        f.close()
    except Exception as ex:
        C.printEx(ex)
        return
    return
    
def grabItut():
    try:
        dr = grab_series_info()
        if (1 > len(dr)):
            return
    except Exception as ex:
        C.printEx(ex)
        return
    try:
        d = {}
        for e in dr:
            r = grab_series(e)
            if (0 < len(r)):
                d[e] = [dr[e], r]
    except Exception as ex:
        C.printEx(ex)
    try:
        for e in dr:
            for ee in d[e][1]:
                fl = grab_file(ee)
                if (0 < len(fl)):
                    d[e][1][ee] = fl
    except Exception as ex:
        C.printEx(ex)
    try:
        html_itut(dr)
    except Exception as ex:
        C.printEx(ex)
    return

if __name__ == '__main__':
    try:
        grabItut()
    except Exception as ex:
        C.printEx(ex)
    pass

