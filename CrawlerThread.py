import queue
import threading
from configparser import ConfigParser
import requests
from lxml import etree
import time
import progressbar
import os
import zipfile
from Rotation import RotationThread

url_queue = queue.Queue()
threads = []
manga_name = ""
cgf = ConfigParser()
cgf.read("crawler.conf")
proxies = dict()
proxies["http"] = cgf.get("connection", "http")
proxies["https"] = cgf.get("connection", "https")
headers = dict()
headers["User-Agent"] = cgf.get("connection", "User-Agent")
local_path = cgf.get("manga", "path")
bar = None
lock = threading.Lock()
count = 0
threads_num = cgf.getint("connection", "threads_num")


class MyThread(threading.Thread):
    def __init__(self, name, rotation):
        super(MyThread, self).__init__()  # 调用父类的构造函数
        self.name = name
        self.rotation = rotation

    def run(self):
        global url_queue
        while True:
            if not url_queue.empty():
                url, content = url_queue.get()
                r = requests.get(url, headers=headers, proxies=proxies)
                if content == "page":
                    self.parse_page(r)
                elif content == "imagePage":
                    self.parse_image_page(r)
                else:
                    self.parse_image(r, url)
            else:
                time.sleep(1)
                if url_queue.empty():
                    break

    def parse_page(self, r):
        global url_queue
        html = etree.HTML(r.text)
        image_list = html.xpath("//div[@class='gdtm']/div/a/@href")
        for imgUrl in image_list:
            url_queue.put((imgUrl, "imagePage"))

    def parse_image_page(self, r):
        global url_queue
        html = etree.HTML(r.text)
        image_src = html.xpath("//div[@id='i3']//img/@src")[0]
        url_queue.put((image_src, "image"))

    def parse_image(self, img, image_src):
        global lock, count
        image_name = image_src.split("/")[-1]
        img_path = local_path + "/" + manga_name + "/" + image_name
        f = open(img_path, 'wb')
        f.write(img.content)
        f.close()
        lock.acquire()
        count += 1
        if count == 1:
            self.rotation.stop()
        bar.update(count)
        lock.release()


def get_manga(url):
    global url_queue, bar, threads, manga_name
    start_time = time.time()
    rotation_thread = RotationThread("rotation", "解析网页...")
    rotation_thread.start()
    r = requests.get(url, headers=headers, proxies=proxies)
    html = etree.HTML(r.text)
    tmp = html.xpath("//p[@class='gpc']/text()")
    res = tmp[0]
    res = res.split()[-2]
    res = res.replace(",", "")  # 去掉数字里面的逗号
    number_of_images = int(res)  # 漫画共有多少张图片
    bar = progressbar.ProgressBar(max_value=number_of_images)
    if manga_name == "": manga_name = url.split("/")[-2]
    if not os.path.exists(local_path + "/" + manga_name):
        os.mkdir(local_path + "/" + manga_name)
    page_list = html.xpath("//table[@class='ptb']//td/a/text()")
    if page_list[-1] == ">":
        max_page = page_list[-2]
    else:
        max_page = page_list[-1]
    url_queue.put((url, "page"))
    for index in range(1, int(max_page)):
        page_url = url + "?p=" + str(index)
        url_queue.put((page_url, "page"))

    rotation_thread.stop()
    rotation_thread = RotationThread("rotation", "下载图片...")
    rotation_thread.start()
    for i in range(threads_num):
        thread = MyThread(manga_name, rotation_thread)
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    # time.sleep(3)
    # 将下载下来的文件打包为一个压缩包
    print("正在打包文件...")
    zipBar = progressbar.ProgressBar(max_value=number_of_images+1)
    zf = zipfile.ZipFile(local_path + "/" + manga_name + ".zip", 'w', zipfile.zlib.DEFLATED)
    for k, file in enumerate(os.listdir(local_path + "/" + manga_name)):
        file_path = local_path + "/" + manga_name + "/" + file
        zf.write(file_path, file)
        zipBar.update(k + 1)
    zf.close()
    zipBar.finish()
    end_time = time.time()
    dur_time = int(end_time - start_time)
    print("共" + str(number_of_images) + "张图片，耗时" + str(dur_time) + "秒")