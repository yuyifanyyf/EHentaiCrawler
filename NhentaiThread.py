from EHentaiCrawler.init import url_queue, lock, headers, proxies
from EHentaiCrawler import init
import threading
import requests
from lxml import etree
import time

count = 0


class NhentaiThread(threading.Thread):
    def __init__(self, name, rotation):
        super(NhentaiThread, self).__init__()  # 调用父类的构造函数
        self.name = name
        self.rotation = rotation

    def run(self):
        while True:
            if not url_queue.empty():
                url, content = url_queue.get()
                r = requests.get(url, proxies=proxies)
                if content == "imagePage":
                    self.parse_image_page(r)
                else:
                    self.parse_image(r, url)
            else:
                time.sleep(1)
                if url_queue.empty():
                    break

    def parse_image_page(self, r):
        html = etree.HTML(r.text)
        image_src = html.xpath("//section[@id='image-container']//img/@src")[0]
        url_queue.put((image_src, "image"))

    def parse_image(self, img, image_src):
        global count
        image_name = image_src.split("/")[-1]
        img_path = init.local_path + "/" + init.manga_name + "/" + image_name
        f = open(img_path, 'wb')
        f.write(img.content)
        f.close()
        lock.acquire()
        count += 1
        if count == 1:
            self.rotation.stop()
        init.bar.update(count)
        lock.release()


def parse_home_page(url):
    r = requests.get(url, proxies=proxies)
    html = etree.HTML(r.text)
    image_list = html.xpath("//a[@class='gallerythumb']/@href")
    for img_url in image_list:
        url_queue.put(("https://nhentai.net" + img_url, "imagePage"))
    tmp = html.xpath("//div[@id='info']/div[1]/text()")
    res = tmp[0]
    res = res.split()[0]
    res = res.replace(",", "")  # 去掉数字里面的逗号
    number_of_images = int(res)  # 漫画共有多少张图片
    name = url.split("/")[-2]
    return name, number_of_images
