import sys
import CrawlerThread as CrawlerThread
import getopt


if __name__ == "__main__":
    url = sys.argv[1]
    try:
        opts, args = getopt.getopt(sys.argv[2:], "n:p:", [])
    except:
        print("python EHCrawler.py <url> -n <manga name> -p <local path>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-n":
            CrawlerThread.manga_name = arg
        if opt == "-p":
            CrawlerThread.local_path = arg
    CrawlerThread.get_manga(url)
    print("complete.")