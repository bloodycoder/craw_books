#coding:utf8
import requests
import re
import os
import pdb
from threading import Thread 
class fetchBook:
    def __init__(self):
        self.header = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}
        """
        self.urls = [
                     'http://txt.rain8.com/txtgw/',
                     'http://txt.rain8.com/txtzj/',
                     'http://txt.rain8.com/txtzx/',
                     'http://txt.rain8.com/txtsh/'
                     ]#添加更多url来
        """
        self.urls = ['http://txt.rain8.com/txtsc/']
        self.rePageIndex = re.compile('list_\d+_\d+.html')
        self.rePageCount = re.compile('<strong>\d+</strong>')
        self.reDownloadGet1 = re.compile('href=.http://txt.rain8.com/plus/xiazai_yfx.php?[^>]+')
        self.reGetTitle = re.compile('<title>.+</title>')
        self.reGetAuthor = re.compile("</small><span>[^>]+")
        self.reBookGetNew = re.compile('')
        self.reBookGetOld = re.compile('')
        self.cnt = 0
    def download(self,downloadUrl,folder,bookname,author,threadid):
        self.cnt+=1
        self.req = requests.get(downloadUrl,headers = self.header)
        folder = folder.decode('gb2312')
        print author
        try:
            author = author.decode('gb2312')
        except:
            author = u'无名氏'
        author = author.replace('|','_')
        posi = './'+folder+'/'+author
        self.createDir(posi)
        f = open(posi+'/'+bookname+'.rar','wb')
        f.write(self.req.content)
        f.close()
        print u'进程(%s)现在下载:'%(str(threadid))+bookname
    def viewAllPage(self,url):
        """
        函数功能为把该栏目下所有页面全过一遍。
        """
        req = requests.get(url,headers = self.header)
        pageIndex = self.rePageIndex.findall(req.text)[0][5:7]
        pageCount = int(self.rePageCount.findall(req.text)[0][8:-9])
        urlToFetch = [url,'list_',pageIndex,'_','1','.html']
        foldname = self.reGetTitle.findall(req.text)[0][7:]
        foldname = foldname.encode('unicode_escape').decode('string_escape')
        foldname = foldname.split('|')[0]
        self.createDir(foldname)
        for page in range(1,pageCount+1):
            urlToFetch[4] = str(page)
            url_to_get = ''.join(urlToFetch)
            req = requests.get(url_to_get,headers = self.header)
            bookNew = self.reBookGetNew.findall(req.text)
            #print x1[0][:-31]
            bookOld = self.reBookGetOld.findall(req.text)
            threadpool = []
            threadid = 0
            for books in bookNew:
                try:
                    threadid +=1
                    downloadUrl,bookName,author = self.fetchDownloadUrl(books[:-31])
                    t = Thread(target = self.download,args=(downloadUrl,foldname,bookName,author,threadid))
                    threadpool.append(t)
                except:
                    print bookName,'下载失败'
            for books in bookOld:
                try:
                    threadid +=1
                    downloadUrl,bookName,author = self.fetchDownloadUrl(books[:-31])
                    t = Thread(target = self.download,args=(downloadUrl,foldname,bookName,author,threadid))
                    threadpool.append(t)
                except:
                    print bookName,'下载失败'
            for t in threadpool:
                t.start()
            for t in threadpool:
                t.join()
        print '下载完成，共下载'+str(self.cnt)+'本'
    def fetchDownloadUrl(self,bookurl):
        req = requests.get(bookurl,headers = self.header)
        result = self.reDownloadGet1.findall(req.text)
        result = result[0][6:-17]
        authorname = self.reGetAuthor.findall(req.text)[0][14:-6].encode('unicode_escape').decode('string_escape')
        req = requests.get(result,headers = self.header)
        bookname = self.reGetTitle.findall(req.text)[0][7:-24]
        downloadurl = self.reDownloadGet1.findall(req.text)[0][6:-17]
        return downloadurl,bookname,authorname
    def fetchAllUrls(self):
        for url in self.urls:
            self.reBookGetNew = re.compile(url+'\d+/\d+.html..class="title".target="_blank"')
            self.reBookGetOld = re.compile(url+'\d+.htm..class="title".target="_blank"')
            self.viewAllPage(url)
    def createDir(self,name):
        try:
            os.makedirs('./'+name)
        except:
            print 'folder exists'
A = fetchBook()
A.fetchAllUrls()
