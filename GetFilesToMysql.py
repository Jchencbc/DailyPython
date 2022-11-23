import re
import pandas as pd
import os
import pymysql


def getfiles(dir_path):
    """遍历文件，获得文件地址列表"""
    file_path_list = []
    for filepath, dirnames, filenames in os.walk(dir_path):  # 遍历文件地址、文件地址列、文件名的三元组
        for filename in filenames:
            file_path = os.path.join(filepath, filename)  # 拼接地址和文件命
            file_path_list.append(file_path)

    return file_path_list  # 返回文件地址列表


def transform(dir_path):
    """解析文件，转化格式，"""
    file_path_list = getfiles(dir_path)
    for file_path in file_path_list:
        try:  # 默认utf-8解析csv
            data = pd.read_csv(file_path)
        except UnicodeDecodeError:  # utf—8不行换用gbk,再不行请修改代码
            data = pd.read_csv(file_path, encoding="gbk")

        col = ['lon', 'lat', 'province']
        data2 = pd.melt(data, id_vars=col, var_name='年份', value_name='数据')  # 列转行
        data2['年份'] = data2['年份'].map(lambda x: re.findall('\d+\.?\d*', x)[0])  # 正则提取年份数字
        # data2['年份'] = data2['年份'].map(lambda x: x.lstrip('y').rstrip(''))
        data2['年份'] = data2['年份'].map(lambda x: int(x))
        replace_word = ['\\', '1979-2020年', '1979-2020', '.csv']
        name = file_path
        for i in replace_word:  # 批量替换文件中不需要保存的名字
            name = name.replace(i, '')
        data2["name"] = name
        data2 = data2.where(data2.notnull(), None)  # 替换nan为mysql可保存的None
        df = data2.values.tolist()  # 数据框转列表
        df2 = []
        for i in df:
            i = tuple(i)
            df2.append(i)
        df2 = tuple(df2)
        print(df2)

        """mysql批量插入"""
        conn = pymysql.connect()  # 填写mysql的连接信息
        cursor = conn.cursor()
        sql = "insert into view_data(lon,lat,province,year,year_data,name) values(%s,%s,%s,%s,%s,%s)"
        # 每一个值都作为一个元组，整个参数集作为一个元组
        param = df2
        cursor.executemany(sql, param)
        # cursor.execute(sql,param)  单行值的插入
        conn.commit()
        # 关闭
        conn.close()
        cursor.close()


if __name__ == '__main__':
    dir_path_list = [r'热相关死亡', r'热相关劳动力损失数据']
    for dir_path in dir_path_list:
        transform(dir_path)
