import requests, time
from reptileBase import ReptileBase
from requests.adapters import HTTPAdapter
s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))

# 获取基础数据
def getData(uid, limit, offset):
    url = f"https://www.tumblr.com/svc/indash_blog?tumblelog_name_or_id={uid}&limit={limit}&offset={offset}&should_bypass_safemode=false&should_bypass_tagfiltering=false"
    headers = {
        'cookie': 'tmgioct=59dc60c94ffa410100176440; rxx=7b3jfe65xmw.vswa8cb&v=1; anon_id=KGKOBVCGRMFZAKTFPNKVNVOBKBDLTUZG; language=%2Czh_CN; logged_in=1; pfp=KTSG6Feba593Ijy4uErqAWsaTyxtqjnCctwfqJZo; pfs=93QUn5pR7ZVi3fN9XAFfYFEZls4; pfe=1515905778; pfu=270308860; pfx=8d7dd8d473a0b89b93f8fe35ab088afb592e0020a63e54e9565bf537dacf6031%231%236765703668; nts=false; capture=fRl7LWkJOoLJlVM2yCc0wzyqNIw; _ga=GA1.2.213989760.1507614730; _gid=GA1.2.248811176.1508809355; yx=7gr3qa9pgbb6n%26o%3D3%26f%3Ds7; devicePixelRatio=1; documentWidth=1276; __utma=189990958.213989760.1507614730.1508809355.1508835475.5; __utmb=189990958.0.10.1508835475; __utmc=189990958; __utmz=189990958.1507614731.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'referer': 'https://www.tumblr.com/search/china+painting',
        'x-requested-with': 'XMLHttpRequest',
        'x-tumblr-form-key': 'fRl7LWkJOoLJlVM2yCc0wzyqNIw',
        'accept - encoding': 'gzip, deflate, br',
    }
    try:
        r = requests.get(url, headers=headers)
        json = r.json()
        if json['meta']['status'] == 200:
            return json['response']['posts']
        else:
            print('Error', json['meta'])
    except Exception as e:
        print(e)
        return False;

def start(uid, limit, offset,reptileBase):  # changan-moon
    data = getData(uid, limit, offset)
    if data:
        for item in data:
            formatData(item,reptileBase)
    start(uid, limit, offset + limit,reptileBase)


def formatData(data,reptileBase):
    id = data['id']  # 帖子ID
    blog = data['blog']
    title = blog['title']
    if reptileBase.is_post(id):
        print(f'{title} 已存在')
        return False

    type = data['type']  # 类型
    description = blog['description']
    updated = blog['updated']
    name = blog['name']  # 用户名称
    post_url = data['post_url']
    slug = data['slug']
    date = time.mktime(time.strptime(data['date'], "%Y-%m-%d %H:%M:%S GMT"))  # 日期转时间戳
    tags = data['tags']  # 标签
    summary = data['summary']  # 简介
    # caption=data['caption']#说明
    notes_count = data['notes']['count']  # 热度
    body = ''
    video_url = ''
    photo_list = []
    cover = ''
    if type == "photo":
        photos = data['photos']  # 图片列表
        photo_list = []
        for photo in photos:
            url = photo['original_size']['url']
            path = reptileBase.download(uid=name, pid=id, url=url)
            if not path:
                print('图集下载错误')
                return False
            photo_list.append(path)
        cover = photo_list[0]  # 封面等于第一个
        print('图片列表下载完成')
    elif type == "video":
        if data['video_type']!="tumblr":
            print('占不支持tumblr以外的视频!')
            return False
        cover = data['thumbnail_url']
        cover = reptileBase.download(uid=name, pid=id, url=cover, name='cover')  # 下载首图
        video_url = data['video_url']
        video_url = reptileBase.download(uid=name, pid=id, url=video_url, name='video')  # 下载视频
        if not video_url:
            print('视频下载错误')
            return False
    elif type == "text":
        body = data['body']
        type = 'article'

    else:
        print('类型<Type {}>未匹配'.format(type))
        return False
    reptileBase.postData(title, type, summary, date, cover=cover, username=name, read=notes_count, tags=tags,post_hash=id, text=body,
             video=video_url, photos=photo_list)

#changan-moon

reptileBase=ReptileBase(True)
start('carry9109', 10, 0,reptileBase)
#carry9109已转发riena-blog