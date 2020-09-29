# -*- coding: utf-8 -*-
'''
Created on 2020-07-14
@author: delong tang
'''

import gc

import Comm as C
import Pp3g as P
import Itut as I

def main_grab(): 
    try:
        P.grab3gpp()
        gc.collect()
    except Exception as ex:
        C.printEx(ex)
    try:
        I.grabItut()
        gc.collect()
    except Exception as ex:
        C.printEx(ex)
    return

if __name__ == '__main__':
    try:
        main_grab()
        C.printInfo('all done!')
    except Exception as ex:
        C.printEx(ex)
    pass