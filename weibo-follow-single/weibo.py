#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import bs4
import time
import re

''' weibo '''

'''
需要更改的参数:
@sub cookie中SUB字段的值
@id 用户首页url: http://weibo.com/{id}/profile?opnav=1&wvr=6&is_all=1
'''

id = ''
sub = ''

COOKIES = {
    'SUB': sub,
}


HEADERS = {
    'Userade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 \
    (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'Connection': 'keep-alive',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}


def show_follow(URL):
    res = requests.get(url=URL, cookies=COOKIES, headers=HEADERS)
    html = res.content.decode('utf-8')
    rex = r'mod_info.*?href=\\"(.*?)\\".*?title=\\"(.*?)\\".*?statu.*?ficon\\">(.*?)<\\/em>'
    datas = re.findall(rex, html, re.DOTALL)

    for idx,data in enumerate(datas):
        url = 'http://weibo.com'+data[0].replace('\\','')
        if data[2] == 'Y':
            status = '【单向关注】'
            print status, data[1], u'主页:'+url



def get_last_page(URL):
    res = requests.get(url=URL, cookies=COOKIES, headers=HEADERS)
    html = res.content
    rex = r'RelationMyfollow__93\\">(.*?)<\\/a>'
    page = re.findall(rex, html, re.DOTALL)
    last_p = page[-2]
    return int(last_p)

if __name__ == '__main__':
    print u'需要手动添加cookie和id哦~'
    URL = 'http://weibo.com/p/100505%s/myfollow?t=1&cfs=&Pl_Official_RelationMyfollow__93_page=1#Pl_Official_RelationMyfollow__93' % id
    last_p = get_last_page(URL)
    for page in range(1,last_p+1):
        URL = 'http://weibo.com/p/100505%s/myfollow?t=1&cfs=&Pl_Official_RelationMyfollow__93_page=%s#Pl_Official_RelationMyfollow__93' % (id,page)
        print page
        show_follow(URL)
