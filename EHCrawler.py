import requests
from lxml import etree
import os
import sys
import getopt
import zipfile
import threading
import time
import queue

headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
proxies = {'http': 'socks5://127.0.0.1:1080', 'https': 'socks5://127.0.0.1:1080'}
mycookie = { "nw":"1" }
mangaName = ""
localPath = r"C:\bt.byr.cn\ehentai"
# localPath = r"C:\bt.byr.cn\ehentai"
UrlQueue = queue.Queue()
threads = []
class MyThread(threading.Thread) :

    def __init__(self, name) :
        super(MyThread, self).__init__()  #调用父类的构造函数
        self.name = name

    def run(self) :
        global UrlQueue
        while True:
            if not UrlQueue.empty():
                url, content = UrlQueue.get()
                r = get(url)
                if content == "page":
                    parsePage(r)
                elif content == "imagePage":
                    parseImagePage(r)
                else:
                    parseImage(r, url)
            else:
                time.sleep(1)
                if UrlQueue.empty():break


def get(url):
    # time.sleep(1)
    r = requests.get(url, headers=headers, proxies=proxies, cookies=mycookie)
    return r

def getManga(url):
    global UrlQueue
    global threads
    global mangaName
    startTime = time.time()
    r = get(url)
    html = etree.HTML(r.text)
    res = html.xpath("//p[@class='gpc']/text()")[0]
    res = res.split()[-2]
    res = res.replace(",", "")#去掉数字里面的逗号
    numberOfImages = int(res)#漫画共有多少张图片
    # mangaName = html.xpath("//h1[@id='gn']/text()")[0]#漫画名称
    # mangaName = mangaName.replace(".", "")#去掉点
    if mangaName == "": mangaName = url.split("/")[-2]
    if not os.path.exists(localPath + "\\" + mangaName):
        os.mkdir(localPath + "\\" + mangaName)
    pageList = html.xpath("//table[@class='ptb']//td/a/text()")
    if pageList[-1] == ">":
        maxPage = pageList[-2]
    else:
        maxPage = pageList[-1]
    # maxPage = pageList[-2]
    # pageList = set(pageList)
    UrlQueue.put((url, "page"))
    for index in range(1, int(maxPage)):
        pageUrl = url + "?p=" + str(index)
        UrlQueue.put((pageUrl, "page"))

    # for pageUrl in pageList:
    #     UrlQueue.put((pageUrl, "page"))
        # parsePage(pageUrl, mangaName)
    for i in range(5):
        thread = MyThread(mangaName)
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    time.sleep(3)
    #将下载下来的文件打包为一个压缩包
    zf = zipfile.ZipFile(localPath + "\\" + mangaName + ".zip", 'w', zipfile.zlib.DEFLATED)
    for file in os.listdir(localPath + "\\" + mangaName):
        filePath = localPath + "\\" + mangaName + "\\" + file
        zf.write(filePath, file)
    zf.close()

    endTime = time.time()
    durTime = int(endTime - startTime)
    print("共" + str(numberOfImages) + "张图片，耗时" + str(durTime) + "秒")

def parsePage(r):
    global UrlQueue
    html = etree.HTML(r.text)
    imageList = html.xpath("//div[@class='gdtm']/div/a/@href")
    for imgUrl in imageList:
        UrlQueue.put((imgUrl, "imagePage"))
        # parseImage(imgUrl, mangaName)

def parseImagePage(r):
    global UrlQueue
    html = etree.HTML(r.text)
    imageSrc = html.xpath("//div[@id='i3']//img/@src")[0]
    UrlQueue.put((imageSrc, "image"))


def parseImage(img, imageSrc):
    global imageQueue
    imageName = imageSrc.split("/")[-1]
    imgPath = localPath + "\\" + mangaName + "\\" + imageName
    f = open(imgPath, 'wb')
    f.write(img.content)
    f.close()
    print(imageName)

if __name__ == "__main__":
    url = sys.argv[1]
    try:
        opts, args = getopt.getopt(sys.argv[2:],"n:p:",[])
    except:
        print("python EHCrawler.py <url> -n <manga name> -p <local path>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-n":mangaName = arg
        elif opt == "-p": localPath = arg
    getManga(url)

    print("complete.")
