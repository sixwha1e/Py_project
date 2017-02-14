#!/usr/bin/python
# -*- coding: utf-8 -*-

#__Author__: sixwhale

import threading
import Queue
import getopt
import sys
import requests
import time
import logging
import lxml.html
from pymongo import MongoClient


conf = {
	'host': '127.0.0.1',
	'port': 27017,
	'colname': '',
	'dbname': ''
}

def usage():
	'''使用方法'''
	print '''spider v1.0 Author: sixwhale
                           ┏━━┓
                           ┃  ┃
    ┏━━━━━━┳━━━━━━━┳━━┳━━━━┛  ┣━━━━━━┳━━━━━┓
    ┃ ━━━━━┫  ┏━━┓ ┣━━┫ ┏━━┓  ┃ ┃━━━━┫  ┏━━┛
    ┣━━━━━ ┃  ┗━━┛ ┃  ┃ ┗━━┛  ┃ ┃━━━━┫  ┃
    ┗━━━━━━┫  ┏━━━━┻━━┻━━━━━━━┻━━━━━━┻━━┛
           ┃  ┃
           ┗━━┛
usage: python spider.py -u [URL] -d [Depth] -f [Logfile] -l [Level] --thread [threadNum] --key [keyword]

-h, --help                    帮助
-u [URL]                      (必选参数)指定爬虫开始地址 以http或https开头
-d [Depth]                    指定爬虫深度 默认为1
-f [Logfile]                  日志记录文件 默认为spider.log
-l [Level]                    日志详细等级(1-5) 数字越大越详细 默认为4
--thread [threadNum]          指定线程数 默认为20
--key [keyword]               关键字 默认为空'''

def initDB(conf):
	'''初始化数据库'''
	global db
	try:
		db = MongoClient(host,port)[conf['dbname']]
	except:
		logging.cratical('[*] 数据库连接失败')


def insert(url, key):
	data = {
		'url': url,
		'key': key,
		'value': None
	}
	try:
		db[conf['colname']].insert_one(data)
	except:
		logging.critical('[*] '+url+'添加失败')


def resquestData(url):
	headers = {
		'Connection': 'keep-alive',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
	}
	try:
		response = requests.get(url, headers=headers, timeout=5)
		html = response.content
	except Exception as e:
		logging.error('[*] 打开 '+ url +' 链接失败'+ e)
		response, html = None
	return response, html 


class MySpider(threading.Thread):
	'''爬虫线程'''
	def __init__(self, workQueue, key=None, timeout=30):
		threading.Thread.__init__(self)

		self.timeout = timeout
		self.setDaemon(True)    #父进程结束 子进程也结束
		self.workQueue = workQueue
		self.rlock = threading.RLock()
		self.key = key
		self.link = None
		self.depth = None
		self.start()

	def run(self):
		while True:
			try:
				#从工作队列中取出一个任务
				self.link, self.depth = self.workQueue.get(timeout=self.timeout)  
			except Queue.Empty:
				logging.error('[*] Queue is empty')
				break
			if self.depth > 0:
				links = self.getLinks()
				self.depth -= 1
				if links:
					global count
					count.append((self.depth,len(links)))
					for l in links:
						self.workQueue.put((l, self.depth))#爬到的子link加入队列中
				self.workQueue.put((self.link,0))#标记这个父link已被完成
			else:
				if key:
					self.insert2DB()
				logging.info(self.link+'    ['+str(self.depth)+']')
			self.workQueue.task_done()#当前这个工作完成后 向队列发送信号


	def getLinks(self):
		response, html = resquestData(self.link)
		linkList = set()
		if html != None:
			data = html.decode('utf8', 'ignore')

			#指定字符串解析成html文档 父节点为<html> data必须是utf-8格式
			doc = lxml.html.document_fromstring(data)
			doc.make_links_absolute(self.link) #将相对路径转换为绝对路径
			links = doc.iterlinks() #筛选出包含链接信息的列表的列表 
			
			tags = ['a', 'frame', 'iframe']
			for link in links: #link有三个元素: tag信息, 子tag(href/src之类), url
				if link[0].tag in tags:
					linkList.add(link[2])
		return linkList

	def insert2DB(self):
		'''设定关键词时 将link和key插入数据库'''
		data = resquestData(self.link)[1]
		if not data:
			return 
		html = data.decode('utf-8', 'ignore')
		if self.key in html:
			self.rlock.acquire() #unlocked 转换为locked 阻塞 插入数据库 
			insert(self.link, self.key)
			self.rlock.release() #locked 转换为 unlocked 释放锁

class ThreadPool(object):
	'''线程池'''
	def __init__(self, threadNum=20):
		self.workQueue = Queue.Queue()
		self.threadList = []
		self.key = None
		self.createThreadPool(threadNum)

	def createThreadPool(self, threadNum):
		for i in range(threadNum):
			thread = MySpider(self.workQueue,self.key) #初始线程池
			self.threadList.append(thread)

	def waitComplete(self):
		#等待所有线程完成
		while len(self.threadList):
			thread = self.threadList.pop()
			if thread.isAlive():  #判断线程是都存活来调用join()
				thread.join() #结束阻塞状态 实际意义是退出线程 

	def addJob(self, job, key=None):
		#job是一个tuple (link,depth)
		self.workQueue.put(job)
		self.key = key

	def getQueue(self):
		return self.workQueue

def mainSpiderFunc(url, threadNum, depth, key):
	'''爬虫主函数'''
	pool = ThreadPool(threadNum)
	pool.addJob((url,depth), key)
	pool.waitComplete()

if __name__ == '__main__':
	#默认参数
	url = None
	depth = 1
	level = 4
	threadNum = 20
	key = None
	logFile = 'spider.log'

	#参数设置
	optlist, args = getopt.getopt(
		sys.argv[1:], #第一个元素是文件名
		'u:d:f:l:h', #加冒号表示后面接参数（u d f l）| h不接参数
		['thread=','dbfile=','key=']) #加等号表示接参数
	for o,a in optlist:
		if o == '-u':
			url = a
		elif o == '-d':
			depth = int(a)
		elif o == '-f':
			logFile = a
		elif o == '-l':
			level = int(a)
		elif o == '--thread':
			threadNum = int(a)
		elif o == '--key':
			key = a
		elif o == '-h':
			usage()
			exit()
	if level < 1 or level > 5 or depth < 1 or threadNum < 1 or not url:
		usage()
		exit()
	if key:
		initDB(conf) #初始化数据库
	loglevel = {
    	1: logging.CRITICAL,
    	2: logging.ERROR,
    	3: logging.WARNING,
    	4: logging.INFO,
    	5: logging.DEBUG
    	}
	logging.basicConfig(filename=logFile, level=loglevel[level])
	count = list()
	num = dict()
	mainSpiderFunc(url, threadNum, depth, key)


	for d in range(depth):
		num[d] = 0
	for i in count:
		d = i[0]
		num[d] += i[1]
	print '[*] the spider is finish:'
	for k in range(depth): # 1:125 2:12506 
		print '[+] level %s: %s pieces' % (k+1, num[depth-k-1])


