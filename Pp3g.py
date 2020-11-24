# -*- coding: utf-8 -*-
'''
Created on 2020-07-14
@author: delong tang
'''

import os
import re
import gc
import zipfile
import pandas as pd

import Comm as C

path_root = './'

path_spec = os.path.join(path_root, 'specs')
url_spec = 'https://www.3gpp.org/ftp/Specs/archive' 
url_spec_rm = 'https://www.3gpp.org/DynaReport/SpecReleaseMatrix.htm'
spec_list = ['21', '22', '23', '24', '28', '29', '32', '33', '35', '36', '37', '38']

path_contrib = os.path.join(path_root, 'contribs')

contrb_list = [ \
                ['TSGR', 'https://www.3gpp.org/ftp/tsg_ran/TSG_RAN', 80], \
                ['TSGR1', 'https://www.3gpp.org/ftp/tsg_ran/WG1_RL1', 96],\
                ['TSGR2', 'https://www.3gpp.org/ftp/tsg_ran/WG2_RL2', 100],\
                ['TSGR3', 'https://www.3gpp.org/ftp/tsg_ran/WG3_Iu', 100],\
                ['TSGR4', 'https://www.3gpp.org/ftp/tsg_ran/WG4_Radio', 90],\
                ['TSGS', 'https://www.3gpp.org/ftp/tsg_sa/TSG_SA', 80],\
                ['TSGS1', 'https://www.3gpp.org/ftp/tsg_sa/WG1_Serv', 80],\
                ['TSGS2', 'https://www.3gpp.org/ftp/tsg_sa/WG2_Arch', 130],\
                ['TSGS3', 'https://www.3gpp.org/ftp/tsg_sa/WG3_Security', 90],\
                ['TSGS5', 'https://www.3gpp.org/ftp/tsg_sa/WG5_TM', 120],\
                ['TSGS6', 'https://www.3gpp.org/ftp/tsg_sa/WG6_MissionCritical', 30]\
              ]

    
def get_href(s):
    tit = ''
    ref = ''
    siz = 0
    try:
        l = s.find_all(name='td')
        if (1 > len(l)):
            return tit, ref, siz
        for e in l:
            ll = e.find_all(name='a')
            if (0 < len(ll)):
                r1 = re.findall('href=".*"',str(e))
                r2 = re.findall('>.*<',str(e))
                ref = r1[0][6:-1]
                tit = r2[0][1:-1]
            else:
                ss = C.getText(e)
                if 'KB' not in ss:
                    continue
                ss = ss.replace(',', '')
                ss = ss.replace('KB', '')
                ss = ss.strip()
                # RP-180600.zip 2018/05/23 7:57 43,9 KB
                # so, '43,9 KB' should be '43.9 KB' 
                siz = int(ss) * 102 
#                siz = int(ss) * 1024
    except Exception as ex:
        C.printEx(ex)
    return tit, ref, siz

    
def get_spec_name(s):
    try:
        ls = s.find_all(name='td')
        if (2 > len(ls)):
            return '',''
        s1 = C.getText(ls[0])
        s1 = s1.strip()
        s2 = C.getText(ls[1])
        s2 = s2.strip()
        if ((0 <len(s1)) and (0 <len(s2))):
            return s1, s2 
    except Exception as ex:
        C.printEx(ex)
    return '',''

def parse_matrix(c, cs):
    try:
        ll = C.getLabal(c, 'tr')
        l = []
        if (1 > len(ll)):
            return []
        for e in ll:
            l1, l2 = get_spec_name(e)
            if (0 < len(l1)):
                l.append([l1, l2])
        return l
    except Exception as ex:
        C.printEx(ex)
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
        C.printEx(ex)
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
        C.printEx(ex)
    return ''

def get_zip_file(p, h, size):
    try:
        if (not os.path.exists(p)):
            sz = 0
        else:
            sz = os.path.getsize(p)
            if  (size <= sz):
                return True  
    except Exception as ex:
        C.printEx(ex)
        return False
    try:
        rt, c, _ = C.getHttp(h)
        if ('zip' not in rt):
            return False
    except Exception as ex:
        C.printEx(ex)
        return False
    try:
        if (len(c) <= sz):
            return True
        f = open(p, 'wb')
        f.write(c)
        f.close()
        C.printInfo('write ' + h)
        return True
    except Exception as ex:
        C.printEx(ex)
    return False

def get_xls_file(p, h, size):
    try:
        if (not os.path.exists(p)):
            sz = 0
        else:
            sz = os.path.getsize(p)
            if  (size <= sz):
                return True  
    except Exception as ex:
        C.printEx(ex)
        return False
    try:
        rt, c, _ = C.getHttp(h)
        if ('xls' not in rt):
            return False
    except Exception as ex:
        C.printEx(ex)
        return False
    try:
        if (len(c) <= sz):
            return True
        f = open(p, 'wb')
        f.write(c)
        f.close()
        C.printInfo('write ' + h)
        return True
    except Exception as ex:
        C.printEx(ex)
    return False

def parse_url(c, s):
    r = []
    try:
        l = C.getLabal(c, 'tr')
        if (1 > len(l)):
            return []
        for e in l:
            l1, l2, sz = get_href(e)
            if (0 < len(l1)):
                r.append([l1, l2, sz])
        return r
    except Exception as ex:
        C.printEx(ex)
    return []

def get_spec_file(p, n, h):
    try:
        rt, c, ct = C.getHttp(h)
        if ('html' not in rt):
            return {}
    except Exception as ex:
        C.printEx(ex)
        return ''
    try:
        l = parse_url(c, ct)
        if (1 > len(l)):
            return ''
    except Exception as ex:
        C.printEx(ex)
        return ''
    try:
        ll = []
        for l1, l2, size in l:
            if ((h in l2) and ('zip' in l2)):
                ll.append([l1, l2])
        ll = sorted(ll, key=lambda k: k[0], reverse = True)
        f = os.path.join(p, ll[0][0])
        if get_zip_file(f, ll[0][1], size):
            return f
    except Exception as ex:
        C.printEx(ex)
    return ''

def get_series(s, p, lm):
    ls = []
    try:
        rt, c, ct = C.getHttp(s)
        if ('html' not in rt):
            return {}
    except Exception as ex:
        C.printEx(ex)
        return []
    try:
        l = parse_url(c, ct)
        if (1 > len(l)):
            return []
    except Exception as ex:
        C.printEx(ex)
        return []
    try:
        for l1, l2, _ in l:
            if s not in l2:
                continue
            sn = get_spec_title(l1, lm)
            if 1 > len(sn):
                continue
            fp = get_spec_file(p, l1, l2) 
            C.printInfo('get ' + l2)
            if 0 < len(fp):
                ls.append([l1,sn,fp])
            gc.collect()
        return ls
    except Exception as ex:
        C.printEx(ex)
    return []

def parse_specs(r, c):
    return

def grab_spec():
    try:
        rt, c, ct = C.getHttp(url_spec_rm)
        if ('html' not in rt):
            return {}
    except Exception as ex:
        C.printEx(ex)
        return {}
    try:
        lm = parse_matrix(c, ct)
        if (1 > len(lm)):
            return {}
    except Exception as ex:
        C.printEx(ex)
        return {}
    try:
        rt, c, ct = C.getHttp(url_spec)
        if ('html' not in rt):
            return {}
    except Exception as ex:
        C.printEx(ex)
        return {}
    try:
        l = parse_url(c, ct)
        if (1 > len(l)):
            return  {}
    except Exception as ex:
        C.printEx(ex)
        return {}
    try:
        d = {}
        for l1, l2, _ in l:
            if '_series' not in l1:
                continue
            for e in spec_list:
                if e in l1:
                    p = os.path.join(path_spec, l1)
                    if (not os.path.exists(p)):
                        os.mkdir(p)
                    C.printInfo('begin to get ' + l1)
                    d[e] = get_series(l2, p, lm)
                    C.printInfo('end to get ' + l1)
                    gc.collect()
        return d
    except Exception as ex:
        C.printEx(ex)
    return {}

str_html = '''<html>
 <head>
  <title>{title_} (powered by delong tang)</title>
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
        C.printEx(ex)
        return
    try:
        s = str_html.format(title_ = '3GPP TS & TR', content_ = s0)
        s = s.encode('utf-8')
        p = os.path.join(path_root, '3GPP_SPEC.html')
        f = open(p, mode = 'wb')
        f.write(s)
        f.close()
    except Exception as ex:
        C.printEx(ex)
    return

def check_meeting_num(t, n):
    try:
        l = t.split('_') 
        if (2 > len(l)):
            return False
        r = re.search("\d+",l[1])
        if r is None:
            return False
        s = r.group(0)
        i = int(s)
        if (i >= n):
            return True 
    except Exception as ex:
        C.printEx(ex)
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
        C.printInfo(f + ' : ' + str(ex))
    return ''

def get_xls_info(p, d):
    try:
        df = pd.read_excel(p, sheet_name='TDoc_List')
    except Exception as ex:
        C.printEx(ex)
        return
    try:
        dt = df.loc[:,['TDoc','Title']].values
    except Exception as ex:
        C.printEx(ex)
        return
    try:
        if (1 > len(dt)):
            return
        for td, ti in dt:
            if td not in d:
                d[td] = ti
            elif (len(ti) > len(d[td])):
                d[td] = ti
    except Exception as ex:
        C.printEx(ex)
        return
    return

def name_del_zip(s):
    ss = 'something wrong!'
    try:
        ss = s.replace('.zip', '')
    except Exception as ex:
        C.printEx(ex)
    return ss

def update_contrib_info(l, d):
    try:
        for i in range(len(l)):
            try:
                s = name_del_zip(l[i][0])
                if s in d:
                    l[i][1] = d[s]
            except Exception as ex:
                C.printEx(ex)
    except Exception as ex:
        C.printEx(ex)
    return

def grab_meeting_file(p, h):
    try:
        rt, c, ct = C.getHttp(h)
        if ('html' not in rt):
            return []
    except Exception as ex:
        C.printEx(ex)
        return []
    try:
        l = parse_url(c, ct)
        if (1 > len(l)):
            return []
    except Exception as ex:
        C.printEx(ex)
        return []
    ll = []
    d = {}
    for l1, l2, size in l:
        try:
            if (h not in l2):
                continue
            if ('zip' in l2):
                f = os.path.join(p, l1)
                if not get_zip_file(f, l2, size):
                    C.printInfo('cannot get ' + l2)
                    continue
                #C.printInfo('get ' + l2)
                s = get_zip_fn(f)
                if (0 < len(s)):
                    ll.append([l1, s, f])
            elif (('TDoc_List_Meeting_' in l2) and ('.xls' in l2)):
                f = os.path.join(p, l1)
                if not get_xls_file(f, l2, size):
                    C.printInfo('cannot get ' + l2)
                    continue
                get_xls_info(f, d)
            gc.collect()
        except Exception as ex:
            C.printEx(ex)
    if (0 < len(d)):
        update_contrib_info(ll, d)
    return ll

def grab_meeting(p, t, h, n):
    try:
        if not check_meeting_num(t, n):
            return []
        pp = os.path.join(p, t)
        if not (os.path.exists(pp)):
            os.mkdir(pp)
    except Exception as ex:
        C.printEx(ex)
        return []
    try:
        rt, c, ct = C.getHttp(h)
        if ('html' not in rt):
            return []
    except Exception as ex:
        C.printEx(ex)
        return []
    try:
        l = parse_url(c, ct)
        if (1 > len(l)):
            return []
    except Exception as ex:
        C.printEx(ex)
        return []
    try:
        for ht, hh, _ in l:
            if (('Docs' in ht) and ('Docs' in hh)):
                return grab_meeting_file(pp, hh)
    except Exception as ex:
        C.printEx(ex)
    return []

def grab_contrib(t, h, n):
    try:
        p = os.path.join(path_contrib, t)
        if not os.path.exists(p):
            os.mkdir(p)
    except Exception as ex:
        C.printEx(ex)
        return {}
    try:
        rt, c, ct = C.getHttp(h)
        if ('html' not in rt):
            return []
    except Exception as ex:
        C.printEx(ex)
        return {}
    try:
        l = parse_url(c, ct)
        gc.collect()
        if (1 > len(l)):
            return  {}
    except Exception as ex:
        C.printEx(ex)
        return {}
    try:
        d = {}
        for mt, mh, _ in l:
            if ((t in mt) and (h in mh)):
                C.printInfo('begin to get ' + mh)
                ll = grab_meeting(p, mt, mh, n)
                C.printInfo('end to get ' + mh)
                if (0 < len(ll)):
                    d[mt] = ll
                gc.collect()
        if (0 < len(d)):
            return d
    except Exception as ex:
        C.printEx(ex)
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
        C.printEx(ex)
        return
    try:
        s = str_html.format(title_ = t, content_ = s0)
        s = s.encode('utf-8')
        p = os.path.join(path_root, t + '.html')
        f = open(p, mode = 'wb')
        f.write(s)
        f.close()
        gc.collect()
    except Exception as ex:
        C.printEx(ex)
    return

def list_spec_dir(p):
    r = []
    if (os.path.isdir(p)):
        l = os.listdir(p)
        for e in l:
            pp = os.path.join(p,e)
            if (os.path.isdir(pp)):
                r = r + list_spec_dir(pp)
            else:
                r.append(pp)
    return r

def get_fn_in_path(p):
    try:
        if os.path.isdir(p):
            return ''
        s = os.path.basename(p)
        if (0 == len(s)):
            return ''
        if '.' not in s:
            return ''
        ss = os.path.splitext(p)
        if (2 == len(ss)):
            return ss[0]
    except Exception as ex:
        C.printEx(ex)
    return ''

def clear_spec(d):
    try:
        lf = list_spec_dir(path_spec)
        ls = []
        for e in d:
            l = d[e] 
            icnt = len(l)
            if (1 > icnt):
                continue
            for _, _, p in l:
                fn = get_fn_in_path(p)
                if (0 < len(fn)):
                    ls.append(fn)
    except Exception as ex:
        C.printEx(ex)
        return
    try:
        for e in lf:
            fn = get_fn_in_path(e)
            if ((0 < len(fn)) and (fn not in ls)):
                os.remove(e) 
    except Exception as ex:
        C.printEx(ex)
    return

def grab3gpp():
    try:
        d = grab_spec()
        if (0 < len(d)):
            html_spec(d)
        clear_spec(d)
        gc.collect()
    except Exception as ex:
        C.printEx(ex)
    try:
        for t, h, n in contrb_list:
            C.printInfo('begin to get ' + h)
            d = grab_contrib(t, h, n)
            C.printInfo('end to get ' + h)
            if (0 < len(d)):
                html_contrib(t, d)
            gc.collect()
    except Exception as ex:
        C.printEx(ex)
    return

def main_grab(): 
    try:
        grab3gpp()
    except Exception as ex:
        C.printEx(ex)
    pass
