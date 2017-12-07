import requests, time, re
from reptileBase import ReptileBase
from requests.adapters import HTTPAdapter
from lxml import html
from sys import argv

s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))


def getVideo(url,date,reptileBase):
    req = requests.post(url)
    htmlStr = req.text
    tree = html.fromstring(htmlStr)

    type = 'video'
    
    
    uid = ''
    matchObj = re.match(r'.*setUploaderName\(\'(.*?)\'.*', htmlStr, re.S | re.I)
    if matchObj:
        uid = matchObj.group(1)  # 用户
    else:
        uid = date

    title = ''
    matchObj = re.match(r'.*setVideoTitle\(\'(.*?)\'.*', htmlStr, re.S | re.I)
    if matchObj:
        title = matchObj.group(1)  # 视频标题

    pid = ''
    matchObj = re.match(r'.*HTML5Player\(\'html5video\'\, \'(.*?)\'.*', htmlStr, re.S | re.I)
    if matchObj:
        pid = matchObj.group(1)  # pid

    if reptileBase.is_post(pid):
        print(f'{title} 已存在')
        return False
    matchObj = re.match(r'.*setVideoUrlHigh\(\'(.*?)\'.*', htmlStr, re.S | re.I)
    if not matchObj:
        print('未找到视频')
        return False


    

    video = matchObj.group(1)  # 视频地址
    print(f'{title[0:20]}')
    cover = ''
    matchObj = re.match(r'.*setThumbUrl169\(\'(.*?)\'.*', htmlStr, re.S | re.I)
    if matchObj:
        cover = matchObj.group(1)  # 视频封面
        cover = reptileBase.download(uid=uid, pid=pid, url=cover, name='cover')

    video = reptileBase.download(uid=uid, pid=pid, url=video, name='video')
    if not video:
        print('视频下载错误')
        return False
    tags = tree.xpath('//span[@class="video-tags"]/a/text()')
    tags.append('xvideos')
    read = tree.xpath('//strong[@id="nb-views-number"]/text()')[0]
    read = int(read.replace(',', ''))

    reptileBase.postData(title, type, '', publish_date=int(time.time()), cover=cover, username=uid,nickname=uid, read=read, tags=tags,
             post_hash=pid, text='', video=video, photos=[])


# typeKey 类型
def start(date, page,reptileBase):

    url=f"https://www.xvideos.com/best/{date}/{page}"
    print(url)
    req = requests.post(url)
    htmlStr = req.text

    tree = html.fromstring(htmlStr)
    a_list = tree.xpath('//div[@class="thumb-block "]/p/a[1]')
    href_list = [a.get('href') for a in a_list]
    print(href_list)
    for href in href_list:
        getVideo(f'https://www.xvideos.com{href}',date,reptileBase)
    print(f'当前页{page}下载完成')

    return start(date, page + 1 , reptileBase)

#yui-hatano-1
if __name__=="__main__":
    date=argv[1]
    reptileBase=ReptileBase(False)
    start(date=date, page=0,reptileBase=reptileBase)
