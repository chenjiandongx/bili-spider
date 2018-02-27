# -*- coding: utf-8 -*-
import threading
import time
import sqlite3
from concurrent import futures

import requests

headers = {
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36'
                  '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
}
total = 1
result = []
lock = threading.Lock()

conn = None
error_msg = []


def run(url):
    # 启动爬虫
    global total
    req = requests.get(url, headers=headers, timeout=6).json()
    time.sleep(0.4)     # 延迟，避免太快 ip 被封
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


def create_db():
    # 创建数据库
    global conn
    conn = sqlite3.connect('data.db')
    conn.execute("""create table if not exists data
                    (id int prinmary key autocrement,
                    aid int,
                    view int,
                    danmaku int,
                    reply int,
                    favorite int,
                    coin int,
                    share int)""")


def save_db():
    # 将数据保存至本地
    global result, conn, error_msg, total
    command = "insert into data values(?, ?, ?, ?, ?, ?, ?, ?);"
    for row in result:
        try:
            conn.execute(command, row)
        except:
            conn.rollback()
            error_msg.append("保存 aid 为: {} 时出现出错".format(row[1]))
    conn.commit()
    result = []


if __name__ == "__main__":
    create_db()
    print("启动爬虫，开始爬取数据")
    for i in range(0, 1981):
        begin = 10000 * i
        urls = ["http://api.bilibili.com/archive_stat/stat?aid={}".format(j)
                for j in range(begin, begin + 10000)]
        with futures.ThreadPoolExecutor(32) as executor:
            executor.map(run, urls)
        save_db()
    for msg in error_msg:
        print(msg)
    conn.close()
