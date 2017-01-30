#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 17 20:51:53 2016

@author: rvuillemot
"""

from bs4 import BeautifulSoup
import urllib.request
import pandas as pd
import json


def scrap(url):
    
    req = urllib.request.Request(url)
    r = urllib.request.urlopen(req)
    soup = BeautifulSoup(r, 'lxml')
    
    days = soup.find_all("div", id="mb6")

    links = days[0].find_all("a")

    result = []
    for l in links:
        print(l['href']) # /calendrier-tunisie.htm
        ## print(l.contents) [<img border="0" src="http://flag.maxifoot-live.com/tn.gif"/>, ' TUNISIE - Ligue 1']
        print(l.contents[1])
        
        r = {}
        r['link'] = l['href'].split('/')[1].split('.')[0]
        r['championship'] = l.contents[1]
        result.append(r)


    return result;
    
if __name__ == "__main__":
    
    # It doesn't matter which URL
    championships = scrap('http://www.maxifoot.fr/calendrier-ligue1-2015-2016.htm')
    
    print(championships)
    print('done')