import threading
import os
import time
import zipfile
import progressbar
from EHentaiCrawler import EhentaiThread, NhentaiThread
from EHentaiCrawler.Rotation import RotationThread
from EHentaiCrawler import init


def get_manga(url):
    start_time = time.time()
    rotation_thread = RotationThread("rotation", "解析网页...")
    rotation_thread.start()
    # number_of_images = 0
    # name = None
    if url.startswith("https://e-hentai"):
        name, number_of_images = EhentaiThread.parse_home_page(url)
    else:
        init.threads_num = 3 # nhentai对线程数比较严格？
        name, number_of_images = NhentaiThread.parse_home_page(url)
    rotation_thread.stop()
    if init.manga_name == "":
        init.manga_name = name
    if not os.path.exists(init.local_path + "/" + init.manga_name):
        os.mkdir(init.local_path + "/" + init.manga_name)
    rotation_thread = RotationThread("rotation", "下载图片...")
    rotation_thread.start()
    init.bar = progressbar.ProgressBar(max_value=number_of_images)
    threads = []
    for i in range(init.threads_num):
        # thread = None
        if url.startswith("https://e-hentai"):
            thread = EhentaiThread.EhentaiThread(init.manga_name, rotation_thread)
        else:
            thread = NhentaiThread.NhentaiThread(init.manga_name, rotation_thread)
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    # 将下载下来的文件打包为一个压缩包
    rotation_thread = RotationThread("rotation", "正在打包文件...")
    print()
    rotation_thread.start()
    zf = zipfile.ZipFile(init.local_path + "/" + init.manga_name + ".zip", 'w', zipfile.zlib.DEFLATED)
    for k, file in enumerate(os.listdir(init.local_path + "/" + init.manga_name)):
        file_path = init.local_path + "/" + init.manga_name + "/" + file
        zf.write(file_path, file)
    zf.close()
    rotation_thread.stop()
    rotation_thread.join()
    end_time = time.time()
    dur_time = int(end_time - start_time)
    print("共" + str(number_of_images) + "张图片，耗时" + str(dur_time) + "秒")
