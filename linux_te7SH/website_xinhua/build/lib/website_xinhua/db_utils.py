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
        {'type_str': '123', 'title': '123', 'author': 'author', 'keywords': 'keywords', 'pulish_region': 'pulish_region', 'date': 123, 'date_str': 'date_str', 'content': 'content', 'source': 'source', 'reposts_count': 123, 'comments_count': 234, 'attitudes_count': 345, 'collects_count': 456, 'source_platform': 'source_platform', 'qriginal_link': 'qriginal_link', 'snowNLP_anay': 'snowNLP_anay', 'emotion_type': 'emotion_type'},
        {'type_str': '123', 'title': '123', 'author': 'author', 'keywords': 'keywords', 'pulish_region': 'pulish_region', 'date': 123, 'date_str': 'date_str', 'content': 'content', 'source': 'source', 'reposts_count': 123, 'comments_count': 234, 'attitudes_count': 345, 'collects_count': 456, 'source_platform': 'source_platform', 'qriginal_link': 'qriginal_link', 'snowNLP_anay': 'snowNLP_anay', 'emotion_type': 'emotion_type'},
        {'type_str': '123', 'title': '123', 'author': 'author', 'keywords': 'keywords', 'pulish_region': 'pulish_region', 'date': 123, 'date_str': 'date_str', 'content': 'content', 'source': 'source', 'reposts_count': 123, 'comments_count': 234, 'attitudes_count': 345, 'collects_count': 456, 'source_platform': 'source_platform', 'qriginal_link': 'qriginal_link', 'snowNLP_anay': 'snowNLP_anay', 'emotion_type': 'emotion_type'}
    ]

    data_obj = {'type_str': '123456', 'title': '12345', 'author': 'author567', 'keywords': 'keywords789', 'pulish_region': 'pulish_region', 'date': 123, 'date_str': 'date_str', 'content': 'content', 'source': 'source', 'reposts_count': 123, 'comments_count': 234, 'attitudes_count': 345, 'collects_count': 456, 'source_platform': 'source_platform', 'qriginal_link': 'qriginal_link', 'snowNLP_anay': 'snowNLP_anay', 'emotion_type': 'emotion_type'}

    insert_one(data_obj)