import requests, os, json, time
import hashlib
import urllib
from download import download as downloadFile
from requests.adapters import HTTPAdapter
s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))

reptile_key='wysj3910'

def md5(str):
    m = hashlib.md5()
    m.update(str.encode('utf-8'))
    return m.hexdigest()


# 下载文件并以hash命名
def download(uid, pid, url, name=None):
    hash=md5(url)

    if not name:
        name = hash
    ext = url[url.rfind('.') + 1:]
    extEnd=ext.rfind('?')
    if extEnd>0:
        ext=ext[:extEnd]
    dirPath = f"../static/{uid}/{pid}/"
    fileName = f"{name}.{ext}"
    postPath= f"/static/{uid}/{pid}/{fileName}"
    savePath = f"{dirPath}{fileName}"
    path = is_download(hash,postPath)
    if path:
        print('文件已下载', path)
        return path

    #创建下载目录
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)
    #下载文件
    res=downloadFile(url,savePath)
    if not res:
        return False
    add_download(hash,url,postPath)
    return postPath


def postData(title, type, summary, publish_date, cover, username, read, tags,post_hash, text='', video='', photos=[]):
    data = {
        'title': title,
        'type': type,
        'summary': summary,
        'cover': cover,
        'publish_date': publish_date,
        'username': username,
        'text': text,
        'video': video,
        'read': read,
        'tags': tags,
        'photos': photos,
        'post_hash':post_hash,
        'key': reptile_key
    }
    r = requests.post('http://localhost:5000/reptile/new_post', data=json.dumps(data))
    resData=r.json()
    if resData['status']==0:
        print('添加贴成功')

#post_id -> post_hash
def is_post(phst_hash):
    r = requests.get(f'http://localhost:5000/reptile/is_post/{phst_hash}')
    resData = r.json()
    return resData['status']==0

#添加下载条目
def add_download(hash,url,path):
    r = requests.post('http://localhost:5000/reptile/add_download', data=json.dumps({'hash':hash,'url':url,'path':path,'key': reptile_key}))
    resData = r.json()
    return resData['status']==0

#检查是否下载 并返回path
def is_download(hash,path):
    r = requests.post(f'http://localhost:5000/reptile/is_download',data=json.dumps({'hash':hash,'path':path}))
    resData = r.json()
    if resData['status']==0:
        return resData['path']
    else:
        return False