# B 站全站视频信息爬虫

B 站我想大家都熟悉吧，其实 B 站的爬虫网上一搜一大堆。不过 **纸上得来终觉浅，绝知此事要躬行**，我码故我在。最终爬取到数据总量为 **1100 万** 条。

#### 开发环境为：Windows10 + python3

### 准备工作

首先打开 B 站，随便在首页找一个视频点击进去。常规操作，打开开发者工具。这次是目标是通过爬取 B 站提供的 api 来获取视频信息，不去解析网页，解析网页的速度太慢了而且容易被封 ip。

勾选 JS 选项，F5 刷新

![bili-0](https://github.com/chenjiandongx/bili-spider/blob/master/images/bili-0.png)

找到了 api 的地址

![bili-1](https://github.com/chenjiandongx/bili-spider/blob/master/images/bili-1.png)

复制下来，去除没必要的内容，得到 https://api.bilibili.com/x/web-interface/archive/stat?aid=15906633 ，用浏览器打开，会得到如下的 json 数据

![bili-2](https://github.com/chenjiandongx/bili-spider/blob/master/images/bili-2.png)

### 动手写码

好了，到这里代码就可以码起来了，通过 request 不断的迭代获取数据，为了让爬虫更高效，可以利用多线程。

#### 核心代码
```
result = []
req = requests.get(url, headers=headers, timeout=6).json()
time.sleep(0.6)     # 延迟，避免太快 ip 被封
try:
    data = req['data']
    video = (
        total,
        data['aid'],        # 视频编号
        data['view'],       # 播放量
        data['danmaku'],    # 弹幕数
        data['reply'],      # 评论数
        data['favorite'],   # 收藏数
        data['coin'],       # 硬币数
        data['share']       # 分享数
    )
    with lock:
        result.append(video)
        if total % 100 == 0:
            print(total)
        total += 1
except:
    pass
```

#### 迭代爬取
```
urls = ["http://api.bilibili.com/archive_stat/stat?aid={}".format(i)
        for i in range(10000)]
with futures.ThreadPoolExecutor(32) as executor:    # 多线程
    executor.map(run, urls)
```

爬取后数据存放进了 MySQL 数据库，总共爬取到了 1100w+ 条数据

前 750w 条数据在这里 [bili.zip](https://github.com/chenjiandongx/bili-spider/blob/master/data/bili.zip)
