import threading
from functools import namedtuple
from concurrent import futures
import time
import csv

import requests


header = ["aid", "view", "danmaku", "reply", "favorite", "coin", "share"]
Video = namedtuple('Video', header)
headers = {
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/56.0.2924.87 Safari/537.36'
}
total = 1
result = []
lock = threading.Lock()


def run(url):
    global total
    req = requests.get(url, headers=headers, timeout=6).json()
    time.sleep(0.25)
    try:
        data = req['data']
        video = Video(
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
            print(total)
            total += 1
    except:
        pass


def save():
    with open("result.csv", "w+", encoding="utf-8") as f:
        f_csv = csv.writer(f)
        f_csv.writerow(header)
        f_csv.writerows(result)


if __name__ == "__main__":
    urls = ["http://api.bilibili.com/archive_stat/stat?aid={}".format(i) for i in range(500000)]
    with futures.ThreadPoolExecutor(8) as executor:
        executor.map(run, urls)
    save()
