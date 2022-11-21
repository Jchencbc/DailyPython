# 爬微博评论
import os
import requests
import pandas as pd
import datetime
from time import sleep
import random
from fake_useragent import UserAgent
import re


def trans_time(v_str):
    """转换GMT时间为标准格式"""
    GMT_FORMAT = '%a %b %d %H:%M:%S +0800 %Y'
    timeArray = datetime.datetime.strptime(v_str, GMT_FORMAT)
    ret_time = timeArray.strftime("%Y-%m-%d %H:%M:%S")
    return ret_time


def tran_gender(gender_tag):
    """转换性别"""
    if gender_tag == 'm':
        return '男'
    elif gender_tag == 'f':
        return '女'
    else:  # -1
        return '未知'


def get_comments(v_weibo_ids, v_comment_file, v_max_page):
    """
	爬取微博评论
	:param v_weibo_id: 微博id组成的列表
	:param v_comment_file: 保存文件名
	:param v_max_page: 最大页数
	:return: None
	"""
    for weibo_id in v_weibo_ids:
        # 初始化max_id
        max_id = '0'
        # 爬取前n页，可任意修改
        for page in range(1, v_max_page + 1):
            wait_seconds = random.uniform(0, 1)  # 等待时长秒
            print('开始等待{}秒'.format(wait_seconds))
            sleep(wait_seconds)  # 随机等待
            print('开始爬取第{}页'.format(page))
            if page == 1:  # 第一页，没有max_id参数
                url = 'https://m.weibo.cn/comments/hotflow?id={}&mid={}&max_id_type=0'.format(weibo_id, weibo_id)
            else:  # 非第一页，需要max_id参数
                if max_id == '0':  # 如果发现max_id为0，说明没有下一页了，break结束循环
                    print('max_id is 0, break now')
                    break
                url = 'https://m.weibo.cn/comments/hotflow?id={}&mid={}&max_id_type=0&max_id={}'.format(weibo_id,
                                                                                                        weibo_id,
                                                                                                        max_id)
            # 发送请求
            ua = UserAgent(verify_ssl=False)
            headers = {
                "user-agent": ua.random,
                # 如果cookie失效，会返回-100响应码
                "cookie": 'FPTOKEN=30$azRFvXqxt4xc4USa1uXoFlup3ctdSA6c7Rl2Wtb4FPvO6G+xFCzATVglSYJMkxu1K0axsk98aZTSuh5jynMTgW0rrU4B8Jf2qzXfAcvSeTyBSyKinzd835G86kHu9kOlDbR/NX5o1pPbiZ7lW8owd/ZEMVu6C/h67RjAwmNKLmOQH5nBe9b2f/82JjRf/Iw8MZgi2Gl08SLZQLMuN79Tf2b3+xrsumSFkH0h82P6uB3Av6mHpCK0gYFG9hNFVGoZLXPdGwU7SzTRCSOf6eDMfRx3goOl8hjpjR1p+z0Cv4kbpnMW0/vLNDOr0hzGegmLoXqo1EUGUtyOJS7cioaunwg8/mNG2Iwtjzy3del+bzaDcjFzlBfi35AOjPZvEIyA|F8+dn1iiXo1HilIflmjdHcKEO4ZHvRMKdnnWiRtM4m0=|10|effa2ce7cac3e9ed60bc9fae716bc57a; WEIBOCN_FROM=1110006030; __bid_n=18494c0811246074b64207; loginScene=102003; SUB=_2A25Ofnz2DeRhGeNH7FYU8ybNzDiIHXVtgQS-rDV6PUJbkdAKLU7ikW1NSpOZYVcxUKwWZPdFYD4k__BPPbVbdeed; _T_WM=95358070374; XSRF-TOKEN=c93d30; mweibo_short_token=146f469944; MLOGIN=1; M_WEIBOCN_PARAMS=oid=4837300565970255&luicode=20000061&lfid=4837300565970255&uicode=20000061&fid=4837300565970255',
                "accept": "application/json, text/plain, */*",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "referer": "https://m.weibo.cn/detail/{}".format(weibo_id),
                "x-requested-with": "XMLHttpRequest",
                "mweibo-pwa": '1',
            }
            r = requests.get(url, headers=headers)  # 发送请求
            print(r.status_code)  # 查看响应码
            print(r.json())  # 查看响应内容
            try:
                max_id = r.json()['data']['max_id']  # 获取max_id给下页请求用
                print(max_id)
                datas = r.json()['data']['data']
            except Exception as e:
                print('excepted: ' + str(e))
                continue
            page_list = []  # 评论页码
            id_list = []  # 评论id
            text_list = []  # 评论内容
            time_list = []  # 评论时间
            like_count_list = []  # 评论点赞数
            source_list = []  # 评论者IP归属地
            user_name_list = []  # 评论者姓名
            user_id_list = []  # 评论者id
            user_gender_list = []  # 评论者性别
            follow_count_list = []  # 评论者关注数
            followers_count_list = []  # 评论者粉丝数
            for data in datas:
                page_list.append(page)
                id_list.append(data['id'])
                dr = re.compile(r'<[^>]+>', re.S)  # 用正则表达式清洗评论数据
                text2 = dr.sub('', data['text'])
                text_list.append(text2)  # 评论内容
                time_list.append(trans_time(v_str=data['created_at']))  # 评论时间
                like_count_list.append(data['like_count'])  # 评论点赞数
                source_list.append(data['source'])  # 评论者IP归属地
                user_name_list.append(data['user']['screen_name'])  # 评论者姓名
                user_id_list.append(data['user']['id'])  # 评论者id
                user_gender_list.append(tran_gender(data['user']['gender']))  # 评论者性别
                follow_count_list.append(data['user']['follow_count'])  # 评论者关注数
                followers_count_list.append(data['user']['followers_count'])  # 评论者粉丝数
            df = pd.DataFrame(
                {
                    '微博id': [weibo_id] * len(time_list),
                    '评论页码': page_list,
                    '评论id': id_list,
                    '评论时间': time_list,
                    '评论点赞数': like_count_list,
                    '评论者IP归属地': source_list,
                    '评论者姓名': user_name_list,
                    '评论者id': user_id_list,
                    '评论者性别': user_gender_list,
                    '评论者关注数': follow_count_list,
                    '评论者粉丝数': followers_count_list,
                    '评论内容': text_list,
                }
            )
            if os.path.exists(v_comment_file):  # 如果文件存在，不再设置表头
                header = False
            else:  # 否则，设置csv文件表头
                header = True
            # 保存csv文件
            df.to_csv(v_comment_file, mode='a+', index=False, header=header, encoding='utf_8_sig')
            print('结果保存成功:{}'.format(v_comment_file))


if __name__ == '__main__':
    weibo_id_list = []  # 指定爬取微博id，可填写多个id
    max_page = 60  # 爬取最大页数
    comment_file = '微博评论.csv'
    # 如果结果文件存在，先删除
    if os.path.exists(comment_file):
        print('csv文件已存在,先删除:', comment_file)
        os.remove(comment_file)
    # 爬取评论
    get_comments(v_weibo_ids=weibo_id_list, v_comment_file=comment_file, v_max_page=max_page)

# df1 = pd.read_excel(r'C:\Users\11561\output.xlsx')
#
# df2 = df1.drop(index=df1.评论数[df1.评论数 < 10].index)
