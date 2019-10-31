import os
import threading
from configparser import ConfigParser
import queue


ehentai_path = os.environ["EHENTAIPATH"]  # 这里要手动配置EHENTAIPATH环境变量，即EHentaiCrawler的路径
cgf = ConfigParser()
cgf.read(ehentai_path + "/crawler.conf")
proxies = dict()
proxies["http"] = cgf.get("connection", "http")
proxies["https"] = cgf.get("connection", "https")
headers = dict()
headers["User-Agent"] = cgf.get("connection", "User-Agent")
url_queue = queue.Queue()
manga_name = ""
threads_num = cgf.getint("connection", "threads_num")
local_path = cgf.get("manga", "path")
bar = None
lock = threading.Lock()