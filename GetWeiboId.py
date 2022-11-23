import os
import re  # 正则表达式提取文本
from jsonpath import jsonpath  # 解析json数据
import requests  # 发送请求
import pandas as pd  # 存取csv文件
import datetime  #
import random
from time import sleep
from fake_useragent import UserAgent


def trans_time(v_str):
    """转换GMT时间为标准格式"""
    GMT_FORMAT = '%a %b %d %H:%M:%S +0800 %Y'
    timeArray = datetime.datetime.strptime(v_str, GMT_FORMAT)
    ret_time = timeArray.strftime("%Y-%m-%d %H:%M:%S")
    return ret_time


def get_weibo_lisdt(v_keyword, v_max_page):
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Mobile Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
    }
    dflist = []
    for page in range(1, v_max_page + 1):
        print("-------开始爬取第{}页——————".format(page))
        url = 'https://m.weibo.cn/api/container/getIndex'
        params = {
            "containerid": "100103type=1&q={}".format(v_keyword),
            "page_type": "searchall",
            "page": page
        }
        r = requests.get(url, headers=headers, params=params)
        cards = r.json()["data"]["cards"]
        text_list = jsonpath(cards, '$..mblog.text')

        dr = re.compile(r'<[^>]+>', re.S)
        text2_list = []

        if not text_list:
            continue
        if type(text_list) == list and len(text_list) > 0:
            for text in text_list:
                text2 = dr.sub('', text)
                text2_list.append(text2)
        time_list = jsonpath(cards, '$..mblog.created_at')
        time_list = [trans_time(v_str=i) for i in time_list]
        author_list = jsonpath(cards, '$..mblog.user.screen_name')
        id_list = jsonpath(cards, '$..mblog.id')
        reposts_count_list = jsonpath(cards, '$..mblog.reposts_count')
        comments_count_list = jsonpath(cards, '$..mblog.comments_count')
        attitudes_count_list = jsonpath(cards, '$..mblog.attitudes_count')
        #         bid_list = jsonpath(cards,'$..mblog.bid')
        #         print(text2_list)

        df = pd.DataFrame(
            {
                '页码': [page] * len(id_list),
                '微博id': id_list,
                #  '微博bid': bid_list,
                '微博作者': author_list,
                '发布时间': time_list,
                '微博内容': text2_list,
                '转发数': reposts_count_list,
                '评论数': comments_count_list,
                '点赞数': attitudes_count_list,
            }
        )
        dflist.append(df)
    return dflist


if __name__ == '__main__':
    keyword = ['']  # 指定爬取微博名称
    max_page = 60  # 爬取最大页数
    # comment_file = '微博评论.csv'
    # # 如果结果文件存在，先删除
    # if os.path.exists(comment_file):
    #     print('csv文件已存在,先删除:', comment_file)
    #     os.remove(comment_file)
    # # 爬取评论
    df = get_weibo_lisdt(keyword, max_page)
    df1 = df[0]
    num = len(df)
    for i in range(num):
        df1 = pd.concat([df1, df[i + 1]])
    df1.to_excel('weibo.xlsx')
