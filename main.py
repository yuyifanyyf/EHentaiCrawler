import sys
from EHentaiCrawler import MyThread
from EHentaiCrawler import init
import getopt


if __name__ == "__main__":
    url = sys.argv[1]
    try:
        opts, args = getopt.getopt(sys.argv[2:], "n:p:", [])
    except:
        print("python main.py <url> -n <manga name> -p <local path>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-n":
            init.manga_name = arg
        if opt == "-p":
            init.local_path = arg
    MyThread.get_manga(url)
    print("complete.")