#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import time
from concurrent import futures

import pymysql
import requests

from bili import headers, connect

conn = pymysql.connect(**connect)
cur = conn.cursor()


total = 1
result = []
lock = threading.Lock()


def run(url):
    # 启动爬虫
    global total
    req = requests.get(url, headers=headers, timeout=6).json()
    time.sleep(0.5)     # 延迟，避免太快 ip 被封
    try:
        data = req['data']
        if data['view'] != "--" and data['aid'] != 0:
            video = (
                data['aid'],        # 视频编号
                data['view'],       # 播放量
                data['danmaku'],    # 弹幕数
                data['reply'],      # 评论数
                data['favorite'],   # 收藏数
                data['coin'],       # 硬币数
                data['share'],      # 分享数
                ""                  # 视频名称（暂时为空）
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
    global cur
    cur.execute("""create table if not exists bili_info
                   (v_aid int primary key,
                    v_view int,
                    v_danmaku int,
                    v_reply int,
                    v_favorite int,
                    v_coin int,
                    v_share int,
                    v_name text)""")


def save_db():
    # 将数据保存至本地
    global result, cur, conn, total
    sql = "insert into bili_info values(%s, %s, %s, %s, %s, %s, %s, %s);"
    for row in result:
        try:
            cur.execute(sql, row)
        except:
            conn.rollback()
    conn.commit()
    result = []


if __name__ == "__main__":
    create_db()
    print("启动爬虫，开始爬取数据")
    for i in range(1, 2015):
        begin = 10000 * i
        urls = ["http://api.bilibili.com/archive_stat/stat?aid={}".format(j)
                for j in range(begin, begin + 10000)]
        with futures.ThreadPoolExecutor(64) as executor:
            executor.map(run, urls)
        save_db()
    print("爬虫结束，共为您爬取到 {} 条数据".format(total))
    conn.close()
