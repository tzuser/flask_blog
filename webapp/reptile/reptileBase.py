import requests, os, json, time
import hashlib
import urllib
from download import download as downloadFile
from requests.adapters import HTTPAdapter
s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))

class ReptileBase(object):
    host='http://localhost:5100/'
    reptile_key='wysj3910'
    isFar=False
    def __init__(self,isFar):
        if isFar :
            self.host='http://liequ.wicp.net/'
        self.isFar=isFar

    def md5(self,str):
        m = hashlib.md5()
        m.update(str.encode('utf-8'))
        return m.hexdigest()

    # 下载文件并以hash命名
    def download(self,uid, pid, url, name=None):
        hash=self.md5(url)

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
        path = self.is_download(hash,postPath)
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

        if(self.isFar):
            self.uploadFile(savePath,postPath)
            

        self.add_download(hash,url,postPath)
        return postPath

    def uploadFile(self,savePath,fileName):
        f=open(savePath, 'rb')
        files = {'file':f }
        data = {
            'fileName': fileName
        }
        try:
            r = requests.post(f'{self.host}reptile/upload', data=data, files=files)
        except requests.exceptions.ConnectionError as e:
            print('上传文件失败 重试',e)
            f.close()
            return uploadFile(self,savePath,fileName)

        resData=r.json()
        if resData['status']==0:
            print('文件上传成功')
            f.close()
            os.remove(savePath)#删除文件
            return True
        else:
            return self.uploadFile(savePath,fileName)
    def postData(self,title, type, summary, publish_date, cover, username, read, tags,post_hash, nickname='',text='', video='', photos=[]):
        data = {
            'title': title,
            'type': type,
            'summary': summary,
            'cover': cover,
            'publish_date': publish_date,
            'username': username,
            'nickname': nickname,
            'text': text,
            'video': video,
            'read': read,
            'tags': tags,
            'photos': photos,
            'post_hash':post_hash,
            'key': self.reptile_key,
        }
        r = requests.post(f'{self.host}reptile/new_post', data=json.dumps(data))
        resData=r.json()
        if resData['status']==0:
            print('添加贴成功')

    #post_id -> post_hash
    def is_post(self,phst_hash):
        r = requests.get(f'{self.host}reptile/is_post/{phst_hash}')
        resData = r.json()
        return resData['status']==0

    #添加下载条目
    def add_download(self,hash,url,path):
        r = requests.post(f'{self.host}reptile/add_download', data=json.dumps({'hash':hash,'url':url,'path':path,'key': self.reptile_key}))
        resData = r.json()
        return resData['status']==0

    #检查是否下载 并返回path
    def is_download(self,hash,path):
        r = requests.post(f'{self.host}reptile/is_download',data=json.dumps({'hash':hash,'path':path}))
        resData = r.json()
        if resData['status']==0:
            return resData['path']
        else:
            return False