import requests,os,threading,time
from requests.adapters import HTTPAdapter
s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))

mutex=threading.Lock()

showList=[]
def showSpeed(list):
    showStr = ""
    listLen=len(list)
    didIndex=0
    for i in list:
        symbol='░'
        if i==1:
            didIndex+=1
            symbol='█'
        elif i==2:
            symbol = '☯'
        showStr += symbol
    print('[{}] {}/{}\r'.format(showStr,didIndex,listLen), end=' ')
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

def download_block(fd, url,path, start, end , block_index):
    global showList
    try:
        with requests.get(url, headers={'Range': f'bytes={start}-{end}'}, timeout=1*64, stream=False) as response:  # 6分钟
            if mutex.acquire():
                fd.seek(start)
                fd.write(response.content)
                mutex.release()
    except Exception as e:
        time.sleep(1)
        showList[block_index] = 2
        showSpeed(showList)
        #重新下载
        return download_block(fd, url,path, start, end , block_index)
    #更新进度条
    showList[block_index]=1
    showSpeed(showList)

#下载文件
def download(url,path,thread_num=20):
    global showList
    download_size=0
    data=getHeaders(url)
    if not data:
        print('下载文件失败')
        return False
    (filesize, type, lastModified)=data
    if filesize < 2*1024*1024:
        thread_num=1
    showList=[0 for i in range(thread_num+1)]
    threads=[]#线程池

    block_size=filesize // thread_num

    #生成并清空文件
    tempf = open(path, 'w')
    tempf.close()
    file_mb=round(filesize/1024/1024,3)#计算文件大小mb
    print(f'开始下载[{file_mb}Mb]:{url}')
    start=0
    end=-1

    showSpeed(showList)
    with open(path, 'rb+') as  f:
        fileno=f.fileno()
        block_index = 0
        while end < filesize - 1:
            start = end + 1
            end = start + block_size - 1
            if end > filesize:
                end = filesize
            dup = os.dup(fileno)
            fd = os.fdopen(dup, 'rb+', -1)
            t = threading.Thread(target=download_block, args=(fd, url,path, start, end ,block_index))
            threads.append(t)
            t.start()
            block_index =block_index+1

        for t in threads:
            t.join()
    return True

if __name__ == '__main__':
    download('https://vtt.tumblr.com/tumblr_obuv4sZh0w1rssthv_r1.mp4','./test.mp4')