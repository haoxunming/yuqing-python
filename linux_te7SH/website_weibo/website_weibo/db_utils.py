from datetime import datetime

import mysql.connector
from mysql.connector import Error
from settings import DATABASE

mysql_info = DATABASE

# 创建连接
connection = mysql.connector.connect(
    host=mysql_info['host'],  # 数据库主机地址
    user=mysql_info['user'],  # 数据库用户名
    password=mysql_info['password'],  # 数据库密码
    database=mysql_info['database']  # 数据库名称
)


def execute_query(query, params=None):
    """ 执行SQL查询或命令 """
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        connection.commit()
        print("查询执行成功")
    except Error as e:
        print(f"执行失败: {e}")
    finally:
        cursor.close()

def insert_one(data):
    table = 'website_data'
    """ 批量插入多条数据 """
    if not data:
        print("没有数据需要插入")
        return

    if not connection.is_connected():
        print("链接数据库失败")
        return
    """ 插入数据 """
    columns = ', '.join(data.keys())
    values = ', '.join(['%s'] * len(data))
    query = f"INSERT INTO {table} ({columns}) VALUES ({values})"
    execute_query(query, tuple(data.values()))


def insert_or_update(data, unique_fields):
    table = 'website_data'

    if not data:
        print("没有数据需要插入或更新")
        return

    if not connection.is_connected():
        print("链接数据库失败")
        return

    data['create_date'] = datetime.now()

    # 构建查询条件
    conditions = ' AND '.join([f"{field}=%s" for field in unique_fields])
    select_query = f"SELECT * FROM {table} WHERE {conditions}"

    # 检查数据是否已存在
    cursor = connection.cursor()
    cursor.execute(select_query, [data[field] for field in unique_fields])
    existing_data = cursor.fetchall()

    if existing_data:
        # 更新数据
        update_set = ', '.join([f"{key}=%s" for key in data.keys() if key not in unique_fields])
        update_query = f"UPDATE {table} SET {update_set} WHERE {conditions}"
        update_params = [data[key] for key in data.keys() if key not in unique_fields] + [data[field] for field in
                                                                                          unique_fields]
        execute_query(update_query, update_params)
        print("数据已更新")
    else:
        # 插入数据
        columns = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        insert_query = f"INSERT INTO {table} ({columns}) VALUES ({values})"
        insert_params = list(data.values())
        execute_query(insert_query, insert_params)
        print("数据已插入")

    cursor.close()


def bulk_insert(data_list):
    table = 'website_data'
    """ 批量插入多条数据 """
    if not data_list:
        print("没有数据需要插入")
        return

    if not connection.is_connected():
        print("链接数据库失败")
        return

    # 获取列名
    columns = ', '.join(data_list[0].keys())
    # 构建占位符
    values_placeholder = ', '.join(['%s'] * len(data_list[0]))
    query = f"INSERT INTO {table} ({columns}) VALUES ({values_placeholder})"

    # 批量执行插入
    cursor = connection.cursor()
    try:
        cursor.executemany(query, [tuple(data.values()) for data in data_list])
        connection.commit()
        print("批量插入成功")
    except Error as e:
        print(f"批量插入失败: {e}")
    finally:
        cursor.close()

if __name__ == '__main__':
    # 准备批量插入的数据
    data_list = [
        {'type_str': '123', 'title': '123', 'author': 'author', 'keywords': 'keywords', 'pulish_region': 'pulish_region', 'date': 123, 'date_str': 'date_str', 'content': 'content', 'source': 'source', 'reposts_count': 123, 'comments_count': 234, 'attitudes_count': 345, 'collects_count': 456, 'source_platform': 1, 'qriginal_link': 'qriginal_link', 'snowNLP_anay': 1, 'emotion_type': 1},
        {'type_str': '123', 'title': '123', 'author': 'author', 'keywords': 'keywords', 'pulish_region': 'pulish_region', 'date': 123, 'date_str': 'date_str', 'content': 'content', 'source': 'source', 'reposts_count': 123, 'comments_count': 234, 'attitudes_count': 345, 'collects_count': 456, 'source_platform': 2, 'qriginal_link': 'qriginal_link', 'snowNLP_anay': 2, 'emotion_type': 2},
        {'type_str': '123', 'title': '123', 'author': 'author', 'keywords': 'keywords', 'pulish_region': 'pulish_region', 'date': 123, 'date_str': 'date_str', 'content': 'content', 'source': 'source', 'reposts_count': 123, 'comments_count': 234, 'attitudes_count': 345, 'collects_count': 456, 'source_platform': 3, 'qriginal_link': 'qriginal_link', 'snowNLP_anay': 3, 'emotion_type': 3}
    ]

    # data_obj = {'type_str': '123456', 'title': '12345', 'author': 'author567', 'keywords': 'keywords789', 'pulish_region': 'pulish_region', 'date': 123, 'date_str': 'date_str', 'content': 'content', 'source': 'source', 'reposts_count': 123, 'comments_count': 234, 'attitudes_count': 345, 'collects_count': 456, 'source_platform': 1, 'qriginal_link': 'qriginal_link', 'snowNLP_anay': 2, 'emotion_type': 2, 'create_date': datetime.now()}

    for data_obj in data_list:
        # insert_one(data_obj)
        insert_or_update(data_obj, ['qriginal_link'])