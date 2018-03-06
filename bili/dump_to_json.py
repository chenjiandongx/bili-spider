#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json

import pymysql

from bili import connect, cols

conn = pymysql.connect(**connect)
cur = conn.cursor()


def get_video_info(order_by):
    global cur
    sql = "select * from bili_info order by {} desc limit 100".format(order_by)
    cur.execute(sql)
    for video in cur.fetchall():
        yield video


def get_json(videos):
    for video in videos:
        d = {cols[i]: video[i] for i in range(8)}
        d.update(v_href="https://www.bilibili.com/video/av{}".format(video[0]))
        yield d


def dump_json(data, filename):
    path = os.path.join("..", "json", "{}.json".format(filename))
    with open(path, "w+", encoding="utf8") as fout:
        json.dump(list(data), fout, ensure_ascii=False)
        print(filename, "DONE!!!")


if __name__ == "__main__":
    for col in cols[1: -1]:
        _data = get_json(get_video_info(col))
        dump_json(_data, col)
