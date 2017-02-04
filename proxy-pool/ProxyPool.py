# -*- coding: utf-8 -*
import requests
import random
import sys
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf-8')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 \
        (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'Upgrade-Insecure-Requests': '1',
    'Connection': 'keep-alive',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}

proxies = []
def get_proxy(page=1):
    global proxies
    for i in range(1, page+1):
        response = requests.get(url='http://www.xicidaili.com/nn/' + str(i), headers=HEADERS)
        soup = BeautifulSoup(response.content, 'lxml')
        ips = soup.findAll('tr')
        for i in range(1, len(ips)):
            try:
                tr = ips[i].findAll('td')
                port = tr[2].contents[0]
                ip = tr[1].contents[0]
                proxies.append(ip+':'+port)
            except:
                pass

def randomchoose():
    if proxies != None:
        return random.choice(proxies)
    else:
        get_proxy()
        return random.choice(proxies)


def removeproxy(proxy):
    if proxy in proxies:
        proxies.remove(proxy)


'''
def func(proxy):
    pass
'''
def func(proxy_temp):
    '''测试函数 可自定义'''
    url = 'http://ip.chinaz.com/getip.aspx'
    res = requests.get(url, proxies=proxy_temp, timeout=3).content
    print res


def do(func):
    proxy = randomchoose()
    proxy_temp = {'http': 'http://'+proxy, 'https': 'https://'+proxy}
    try:
        func(proxy_temp)
    except Exception,e:
    	removeproxy(proxy)
        print e

if __name__ == '__main__':
    get_proxy()
    for i in range(200):
        do(func)