import requests,os,threading,math
from tqdm import tqdm
from requests.adapters import HTTPAdapter
s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))

#获取文件信息
def getHeaders(url):
    try:
        r = requests.get(url, stream=True, timeout=60)# 1分钟
    except Exception as e:
        print('获取文件信息失败')
        return False
    # 获取文件长度
    length = int(r.headers['Content-Length'])  # 字节
    type = r.headers['Content-Type']  # 类型
    lastModified = '' #r.headers['Last-Modified']
    return (length,type,lastModified)

def download_block(fd,url,index,block_size,conentLength):
    start=block_size*index
    end=start+block_size
    if start!=0:
        start+=1
    if end>conentLength:
        end=conentLength
    headers={'Range':f'bytes={start}-{end}'}
    try:
        r = requests.get(url, headers=headers, timeout=360)  # 6分钟
    except Exception as e:
        print('段落下载失败')
        return False
    fd.seek(start)
    fd.write(r.content)


#下载文件
def download(url,path,thread_num=10):
    data=getHeaders(url)
    if not data:
        print('下载文件失败')
        return False
    (length, type, lastModified)=data
    threads=[]#线程池
    block_size=0
    #文件小于521k则不使用多线程
    if length<512*1024:
        block_size=length
        thread_num=1

    if length>10*1024*1024:
        thread_num=20

    if block_size==0:
        block_size=math.ceil(length/thread_num) #获取块的大小
    #生成并清空文件
    tempf = open(path, 'w')
    tempf.close()
    file_mb=round(length/1024/1024,3)
    print(f'开始下载[{file_mb}Mb]:{url}')
    with open(path, 'rb+') as  f:
        fileno=f.fileno()
        for index in range(thread_num):
            dup = os.dup(fileno)
            fd = os.fdopen(dup, 'rb+', -1)
            t=threading.Thread(target=download_block, args=(fd,url, index, block_size,length))
            t.start()
            threads.append(t)
        for t in tqdm(threads):
            t.join()
    return True