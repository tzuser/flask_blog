import requests,os,threading,math
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
            # 调用下载事件
            if onDownload:
                onDownload(end-start)
    except Exception as e:
        print("段落下载失败", e,start, end)
        f = open('error.txt', 'a+')
        f.write(f'{url},{path},{start},{end}\n')
        f.close()
    # try:
    #     with requests.get(url, headers={'Range':f'bytes={start}-{end}'}, timeout=1*60, stream=True) as response:  # 6分钟
    #         chunk_size = 1024  # 单次请求最大值
    #         content=None
    #         for data in response.iter_content(chunk_size=chunk_size):
    #             content=content+data if content else data
    #             current_size+=len(data)
    #             #调用下载事件
    #             if onDownload:
    #                 onDownload(len(data))
    #         fd.seek(content)
    #         fd.write(data)
    # except Exception as e:
    #     print(e)
    #     print("段落下载失败",start,end)
    #     f=open('error.txt', 'a+')
    #     f.write(f'{url},{path},{current_size},{end}\n')
    #     f.close()


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
    threading.BoundedSemaphore(thread_num)

    block_size=filesize // thread_num

    #生成并清空文件
    tempf = open(path, 'w')
    tempf.close()
    file_mb=round(filesize/1024/1024,3)#计算文件大小mb
    print(f'开始下载[{file_mb}Mb]:{url}')
    start=0
    end=-1
    #进度条
    pbar = tqdm(total=filesize)
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
def errorDownload():
    errorFile=open("error.txt", "r")
    lines = errorFile.readlines()
    errorFile.close()
    index=0
    while len(lines)>0:
        line=lines.pop(0)
        (url,path,start,end)=line.split(',')
        end = end.replace('\n', '')
        print(url,path,start,end)
        with open(path, 'rb+') as  f:
            fileno = f.fileno()
            dup = os.dup(fileno)
            fd = os.fdopen(dup, 'rb+', -1)
            download_block(fd, url, path, int(start), int(end))
            errorFile = open("error.txt", "w")
            errorFile.writelines(lines)
            errorFile.close()

if __name__=="__main__":
    errorDownload()
    #download('https://vtt.tumblr.com/tumblr_obuv4sZh0w1rssthv_r1.mp4','./test.mp4')