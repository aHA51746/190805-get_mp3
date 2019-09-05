#coding:utf-8
#不支持多线程
import requests
from bs4 import BeautifulSoup as bs
import json
import wget
import time
import pymysql

class DataBase():

	def __init__(self):

		self.db = pymysql.connect('47.106.36.114', 'root', 'Qzy1996a', 'proxy')
		self.cursor = self.db.cursor()

	def clouse(self):

		self.db.close()
		self.cursor.close()

	def find(self):

		sql = 'select ip,port from 66_proxy where success>95 order by success desc'
		self.cursor.execute(sql)
		result = self.cursor.fetchall()
		if result == ():
			result = False
		return result

def getPage(url, method, session, page=1 , r=None, proxy=(0,0)):#请求获取html
   
    headers = {
        "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
        "Referer": r
    }
    proxies = {
        "http": "http://%s:%s" %proxy,
        'https': "https://%s:%s" %proxy   	
    }
    data = {
        "bookId": "10956",
        "isPay": "0",
        "page": page,
        "ha": "t",
        "mid": "12500",    
    }
    if method == 'get':
        res = session.get(url, headers=headers)
        return res
    elif method == 'post':
        times = 1
        while True:
            res = session.post(url, headers=headers, data=data, timeout=2)
            if res.status_code == 200:
                return res
            time.sleep(times)#重试获取
            times += 1
            if times == 3:
                print('%s,服务器拒绝访问了！' %url)
                return False       
    else:
        print('方法错误')
        return None

def mediaUrl(html):#返回每集url列表
    soup = bs(html)
    temp = soup.select(".plist > ul > li")
    ml = []
    for url in temp:
        t = url.find('a').get("href")
        ml.append(t)
    return ml
   
def getName(html):
	soup = bs(html)
	name = soup.find('h1').text
	return name

def glinkUrl(html):#提取中间url
    j = json.loads(html)
    return j["url"] 

def realUrl():
    session = requests.Session()
    url = 'https://ting55.com/book/10956'#选集页面
    html = getPage(url,'get',session).text
    mList = mediaUrl(html)
    total = len(mList)#获取总集数
    fUrl = 'https://pp.ting55.com/'#开始url
    mUrl = 'https://ting55.com/glink'#通过次网站获取中间url
    db = DataBase()
    proxies = db.find()
    for i in range(1,total+1):
        murl = url + '-' + str(i)#获取每集页面
        html = getPage(murl,'get',session).text
        name = getName(html)
        html = getPage(mUrl, 'post', session, page=i, r=murl).text
        lUrl = glinkUrl(html)#获取真实地址
        print("正在获取%s " %lUrl)
        yield (lUrl, name)
        time.sleep(2)
        
            
class myWget():#下载日志
    
    def __init__(self):
        self.count = 1
        
    def download(self, url, name):
        try:
            filename = wget.download(url, out=name+'.mp3')
            self.write(filename,'下载成功')
        except Exception as e:
            self.write(url,e)
        finally:
            self.count += 1
    
    def write(self,url,e):
        with open('d_log.txt','a') as f:
            info = str(self.count)+' '+url + " "+str(e)+"\n"
            f.write(info)

            
def main():
    w = myWget()
    urls= realUrl()
    for i in urls:
    	w.download(i[0], i[1])

if __name__ == "__main__":
    main()
    
        

