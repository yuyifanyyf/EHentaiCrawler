import threading
import requests
import time
from lxml import etree
from EHentaiCrawler.init import url_queue, lock, local_path, headers, proxies
from EHentaiCrawler import init


count = 0


class EhentaiThread(threading.Thread):
    def __init__(self, name, rotation):
        super(EhentaiThread, self).__init__()  # 调用父类的构造函数
        self.name = name
        self.rotation = rotation

    def run(self):
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
        html = etree.HTML(r.text)
        image_list = html.xpath("//div[@class='gdtm']/div/a/@href")
        for imgUrl in image_list:
            url_queue.put((imgUrl, "imagePage"))

    def parse_image_page(self, r):
        html = etree.HTML(r.text)
        image_src = html.xpath("//div[@id='i3']//img/@src")[0]
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
    """
    :param url:
    :return: [manga_name, pic_num]
    """
    r = requests.get(url, headers=headers, proxies=proxies)
    html = etree.HTML(r.text)
    tmp = html.xpath("//p[@class='gpc']/text()")
    res = tmp[0]
    res = res.split()[-2]
    res = res.replace(",", "")  # 去掉数字里面的逗号
    number_of_images = int(res)  # 漫画共有多少张图片
    name = url.split("/")[-2]
    page_list = html.xpath("//table[@class='ptb']//td/a/text()")
    if page_list[-1] == ">":
        max_page = page_list[-2]
    else:
        max_page = page_list[-1]
    url_queue.put((url, "page"))
    for index in range(1, int(max_page)):
        page_url = url + "?p=" + str(index)
        url_queue.put((page_url, "page"))
    return name, number_of_images
