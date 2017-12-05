import requests, time, re
from reptileBase import ReptileBase
from requests.adapters import HTTPAdapter
from lxml import html
from sys import argv

s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))


def getVideo(url,uid,reptileBase):
    req = requests.post(url)
    htmlStr = req.text
    tree = html.fromstring(htmlStr)

    type = 'video'
    uid = uid
    nickname = re.sub(r'-', ' ', uid)
    nickname = re.sub(r'[0-9]','',nickname)

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

    reptileBase.postData(title, type, '', publish_date=int(time.time()), cover=cover, username=uid,nickname=nickname, read=read, tags=tags,
             post_hash=pid, text='', video=video, photos=[])


# typeKey 类型
def start(name, page, typeKey,reptileBase):
    # pornstar 明星 best 用户
    types = ['pornstar', 'best']
    url=f"https://www.xvideos.com/profiles/{name}/videos/{types[typeKey]}/{page}"
    print(url)
    req = requests.post(url)
    htmlStr = req.text
    htmlStr = htmlStr.replace("<script>document.write(xv.thumbs.replaceThumbUrl('", '')
    htmlStr = htmlStr.replace("'));</script>", '')

    tree = html.fromstring(htmlStr)
    page_a_list = tree.xpath('//li[last()]/a/text()')

    if page_a_list and page_a_list[0] == "Next":
        print('存在更多页面')
        page_a_list = tree.xpath('//li[last()-1]/a/text()')
    a_list = tree.xpath('//div[@class="thumb-block "]/p/a[1]')
    href_list = [a.get('href') for a in a_list]
    pages=0
    if page_a_list!=[]:
        pages = int(page_a_list[0]) - 1  # 总页面

    for href in href_list:
        getVideo(f'https://www.xvideos.com{href}',name,reptileBase)
    print(f'当前页{page}/{pages}下载完成')
    if page < pages:
        return start(name, page + 1, typeKey , reptileBase)

#yui-hatano-1
if __name__=="__main__":
    name=argv[1]
    typeKey=int(argv[2])
    reptileBase=ReptileBase(False)
    start(name=name, page=0, typeKey=typeKey,reptileBase=reptileBase)
