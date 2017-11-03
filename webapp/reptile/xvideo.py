import requests, time,re
from reptileBase import md5,download,downloadFile,postData,add_download,is_download,is_post
from requests.adapters import HTTPAdapter

from lxml import html
s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))

def getVideo(url):
    req = requests.post(url)
    htmlStr = req.text
    tree = html.fromstring(htmlStr)

    type = 'video'
    uid = 'xvideos'

    title = ''
    matchObj = re.match(r'.*setVideoTitle\(\'(.*?)\'.*', htmlStr, re.S | re.I)
    if matchObj:
        title = matchObj.group(1)  # 视频标题

    pid = ''
    matchObj = re.match(r'.*HTML5Player\(\'html5video\'\, \'(.*?)\'.*', htmlStr, re.S | re.I)
    if matchObj:
        pid = matchObj.group(1)  # pid

    if is_post(pid):
        print(f'{title} 已存在')
        return False
    matchObj = re.match(r'.*setVideoUrlHigh\(\'(.*?)\'.*', htmlStr, re.S | re.I)
    if not matchObj:
        print('未找到视频')
        return False
    video = matchObj.group(1)  # 视频地址

    cover = ''
    matchObj = re.match(r'.*setThumbUrl169\(\'(.*?)\'.*', htmlStr, re.S | re.I)
    if matchObj:
        cover = matchObj.group(1)  # 视频封面
        cover = download(uid=uid,pid=pid,url=cover, name='cover')

    video = download(uid=uid, pid=pid, url=video, name='video')
    if not video:
        print('视频下载错误')
        return False
    tags=tree.xpath('//span[@class="video-tags"]/a/text()')
    read=tree.xpath('//strong[@id="nb-views-number"]/text()')[0]
    read=int(read.replace(',',''))

    postData(title, type, '',  publish_date=int(time.time()), cover=cover, username=uid, read=read, tags=tags, post_hash=pid,text='',video=video, photos=[])


def start(name,page):
    req=requests.post(f"https://www.xvideos.com/profiles/{name}/videos/pornstar/{page}")
    htmlStr=req.text
    htmlStr=htmlStr.replace("<script>document.write(xv.thumbs.replaceThumbUrl('",'')
    htmlStr=htmlStr.replace("'));</script>",'')

    tree = html.fromstring(htmlStr)
    page_a_list=tree.xpath('//li[last()]/a/text()')
    script_list=tree.xpath('//script/text()')
    a_list=tree.xpath('//div[@class="thumb-block "]/p/a[1]')
    href_list =[a.get('href') for a in a_list]
    pages=int(page_a_list[0])-1#总页面

    for href in href_list:
        getVideo(f'https://www.xvideos.com{href}')
    print(f'当前页{page}下载完成')
    if page<pages:
        start(name,page+1)

start('yui-hatano-1',0)