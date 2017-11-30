import requests,os,threading,math,time
from tqdm import tqdm
from requests.adapters import HTTPAdapter
s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))

mutex=threading.Lock()

#获取文件信息
def getHeaders(url):
    try:
        r = requests.get(url,stream=True, timeout=60)# 1分钟
    except Exception as e:
        print('获取文件信息失败')
        return False
    # 获取文件长度
    filesize = int(r.headers['Content-Length'])  # 字节
    type = r.headers['Content-Type']  # 类型
    lastModified = '' #r.headers['Last-Modified']
    return (filesize,type,lastModified)

def download_block(fd, url,path, start, end,onDownload=None):
    try:
        with requests.get(url, headers={'Range': f'bytes={start}-{end}'}, timeout=1*64, stream=False) as response:  # 6分钟
            if mutex.acquire():
                fd.seek(start)
                fd.write(response.content)
                mutex.release()
    except Exception as e:
        print("{}-{}重新下载 {}".format(start,end,e))
        time.sleep(1)
        #重新下载
        return download_block(fd, url,path, start, end,onDownload)
    try:
        # 调用下载事件
        if onDownload:
            onDownload(end - start)
    except RuntimeError as e:
        print('更新进度条失败')
#下载文件
def download(url,path,thread_num=20):
    download_size=0
    data=getHeaders(url)
    if not data:
        print('下载文件失败')
        return False
    (filesize, type, lastModified)=data
    if filesize < 2*1024*1024:
        thread_num=1

    threads=[]#线程池
    # 信号量，同时只允许3个线程运行
    #threading.BoundedSemaphore(thread_num)

    block_size=filesize // thread_num

    #生成并清空文件
    tempf = open(path, 'w')
    tempf.close()
    file_mb=round(filesize/1024/1024,3)#计算文件大小mb
    print(f'开始下载[{file_mb}Mb]:{url}')
    start=0
    end=-1
    #进度条

    try:
        pbar = tqdm(total=filesize)
    except RuntimeError as e:
        print('更新进度条失败')

    with open(path, 'rb+') as  f:
        fileno=f.fileno()
        while end < filesize - 1:
            start = end + 1
            end = start + block_size - 1
            if end > filesize:
                end = filesize
            dup = os.dup(fileno)
            fd = os.fdopen(dup, 'rb+', -1)
            t = threading.Thread(target=download_block, args=(fd, url,path, start, end,pbar.update))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
    return True

#download('https://vtt.tumblr.com/tumblr_obuv4sZh0w1rssthv_r1.mp4','./test.mp4')