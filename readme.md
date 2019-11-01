# EHentaiCrawler
一个简单的漫画下载工具，目前支持ehentai和nhentai
## 用法
需要配置环境变量``EHENTAIPATH``，值为项目目录的路径
```
python main.py <url> -n <manga_name> -p <local_path>
url: 漫画地址
manga_name: 指定漫画保存名称，不指定的话会生成一个默认的名称
local_path: 指定漫画本地保存路径，不指定的话会保存到默认路径
```
## 配置文件
- http: http代理
- https: https代理
- threads_num: 下载线程数
- path: 默认下载路径