# mysql_tool.py

import mysql.connector
from mysql.connector import Error

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from transformers import BertTokenizer, BertForSequenceClassification, pipeline
import torch
import os
# es_tool.py

from elasticsearch import Elasticsearch, helpers

class ElasticsearchTool:
    def __init__(self, hosts, port, user, password, index_name):
        self.hosts = hosts
        self.port = port
        self.user = user
        self.password = password
        self.index_name = index_name
        self.es = None

    def connect(self):
        """ 连接到Elasticsearch """
        try:
            # self.es = Elasticsearch(self.hosts)
            #self.es = Elasticsearch([{"host": self.hosts, "port": self.port, "scheme": "https"}], http_auth=(self.user, self.password), verify_certs=False)
            self.es = Elasticsearch([{"host": self.hosts, "port": self.port, "scheme": "https"}], http_auth=(self.user, self.password), verify_certs=False)

            if self.es.ping():
                print("Elasticsearch连接成功")
            else:
                print("Elasticsearch连接失败")
        except Exception as e:
            print(f"连接失败: {e}")

    def close(self):
        """ 关闭连接 """
        if self.es:
            self.es.close()
            print("Elasticsearch连接已关闭")

    def insert_update_doc_by_url(self, dict_data):
        # 检查索引是否存在
        if not self.es.indices.exists(index=self.index_name):
            # 如果索引不存在，则创建索引
            self.es.indices.create(index=self.index_name, body={
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0
                },
                "mappings": {
                    "properties": {
                        "title": {"type": "text"},
                        "url": {"type": "keyword"}
                    }
                }
            })
        # 定义查询条件，通过 url 字段找到特定文档
        query_body = {
            "query": {
                "term": {
                    "qriginal_link.keyword": dict_data['qriginal_link']
                }
            }
        }

        # 执行搜索操作，获取所有文档
        response = self.es.search(index=self.index_name, body=query_body, size=10000)

        if response['hits']['total']['value'] > 0:
            # 更新文档
            for hit in response['hits']['hits']:
                source = hit['_source']

                source['type_str'] = dict_data['type_str']
                source['title'] = dict_data['title']
                source['author'] = dict_data['author']
                source['keywords'] = dict_data['keywords']
                source['pulish_region'] = dict_data['pulish_region']
                source['date'] = dict_data['date']
                source['date_str'] = dict_data['date_str']
                source['content'] = dict_data['content']
                source['source'] = dict_data['source']
                source['reposts_count'] = dict_data['reposts_count']
                source['comments_count'] = dict_data['comments_count']
                source['attitudes_count'] = dict_data['attitudes_count']
                source['collects_count'] = dict_data['collects_count']
                source['source_platform'] = dict_data['source_platform']
                source['qriginal_link'] = dict_data['qriginal_link']
                source['snowNLP_anay'] = dict_data['snowNLP_anay']
                source['emotion_type'] = dict_data['emotion_type']

                # 更新文档
                update_body = {
                    "doc": {
                        "type_str": dict_data['type_str'],
                        "title": dict_data['title'],
                        "author": dict_data['author'],
                        "keywords": dict_data['keywords'],
                        "pulish_region": dict_data['pulish_region'],
                        "date": dict_data['date'],
                        "date_str": dict_data['date_str'],
                        "content": dict_data['content'],
                        "source": dict_data['source'],
                        "reposts_count": dict_data['reposts_count'],
                        "comments_count": dict_data['comments_count'],
                        "attitudes_count": dict_data['attitudes_count'],
                        "collects_count": dict_data['collects_count'],
                        "source_platform": dict_data['source_platform'],
                        "qriginal_link": dict_data['qriginal_link'],
                        "snowNLP_anay": dict_data['snowNLP_anay'],
                        "emotion_type": dict_data['emotion_type']
                    }
                }

                # 执行更新操作
                self.es.update(index=self.index_name, id=hit['_id'], body=update_body)
            print("更新完成")
        else:
            # 新增
            try:
                # 插入文档
                self.es.index(index=self.index_name, document=dict_data)
                print(f"文档插入成功: {dict_data}")
            except Exception as e:
                print(f"插入文档时发生错误: {e}")

    def bulk_insert(self, data_list):
        """ 批量插入数据 """
        if not data_list:
            print("没有数据需要插入")
            return

        actions = [
            {
                "_index": self.index_name,
                "_source": data
            }
            for data in data_list
        ]

        try:
            response = helpers.bulk(self.es, actions)
            print(f"批量插入成功: {response}")
        except Exception as e:
            print(f"批量插入失败: {e}")

    def search(self, query):
        """ 查询数据 """
        try:
            response = self.es.search(index=self.index_name, body=query)
            return response
        except Exception as e:
            print(f"查询失败: {e}")
            return None



class MySQLTool:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        """ 连接到MySQL数据库 """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("数据库连接成功")
        except Error as e:
            print(f"连接失败: {e}")

    def close(self):
        """ 关闭数据库连接 """
        if self.connection.is_connected():
            self.connection.close()
            print("数据库连接已关闭")

    def fetch_data(self, query, params=None):
        """ 查询数据并返回结果 """
        # cursor = self.connection.cursor()
        cursor = self.connection.cursor(dictionary=True)  # 设置游标类型为字典游标
        try:
            cursor.execute(query, params)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"查询失败: {e}")
        finally:
            cursor.close()

    def fetch_data_update(self, query, params=None):
        """ 查询数据并返回结果 """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            self.connection.commit()
            print(f"Updated {cursor.rowcount} rows.")
        except Error as e:
            print(f"修改失败: {e}")
        finally:
            cursor.close()

def predict_sentiment(text):
    os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

    # 1. 加载预训练的BERT模型和tokenizer
    model = BertForSequenceClassification.from_pretrained('bert-base-chinese', num_labels=2)
    tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')

    # 切换模型到评估模式
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()
    # 对输入文本进行tokenization
    inputs = tokenizer(text, return_tensors="pt", padding="max_length", truncation=True, max_length=128)

    # 将输入转移到GPU（如果有）
    inputs = {k: v.to(device) for k, v in inputs.items()}

    # 禁用梯度计算（推理模式）
    with torch.no_grad():
        outputs = model(**inputs)

    # 获取模型的输出logits
    logits = outputs.logits

    # 获取预测类别，0表示负面，1表示正面
    prediction = torch.argmax(logits, dim=-1).item()

    print(prediction)

    # 返回预测的情感结果
    if prediction == 1:
        return "正面"
    else:
        return "负面"

# main.py
def main():
    emotional_data_type = {}
    # 数据库连接参数
    host = '127.0.0.1'
    user = 'public_sentiment'
    password = 'df32KX2fseEaPANK'
    database = 'public_sentiment'

    # 创建MySQLTool实例并连接数据库
    db_tool = MySQLTool(host, user, password, database)
    db_tool.connect()

    query_one = "select id,label,value from t_dict_data where dict_type = 'emotional_attribute'"
    data_one = db_tool.fetch_data(query_one)
    for row_one in data_one:
        if row_one['label'] not in emotional_data_type:
            emotional_data_type[row_one['label']] = row_one['value']

    if emotional_data_type:
        emotional_data_type = emotional_data_type

    # 读取数据
    query = "SELECT * FROM website_data where flag_type != 1"
    data = db_tool.fetch_data(query)

    # 获取数据集合
    data_es_list = []
    # 获取数据ID
    data_update_id = []
    # 循环处理每条数据
    if not data:
        # 关闭数据库连接
        db_tool.close()
        return
    if data:
        for row in data:
            # 使用BERT模型进行分析
            type_str = predict_sentiment(row['content'])
            if type_str:
                print(f"更新前==={row['snowNLP_anay']}")
                if row['snowNLP_anay'] and row['snowNLP_anay'] != 2:
                    snowNLP_anay = emotional_data_type[type_str]
                    row['snowNLP_anay'] = snowNLP_anay
                    print(f"更新后==={row['snowNLP_anay']}")
            data_es_list.append(row)
            data_update_id.append(row['id'])
            print(f"ID: {row['id']}, Label: {type_str}")

        if data_update_id:
            # 构建 IN 子句
            id_placeholders = ', '.join(['%s'] * len(data_update_id))
            query = f"UPDATE website_data SET flag_type = 1 WHERE id IN ({id_placeholders})"
            db_tool.fetch_data_update(query, data_update_id)

        # 关闭数据库连接
        db_tool.close()

        if data_es_list:
            es_main(data_es_list)

# main.py
def es_main(data_list):
    # Elasticsearch连接参数
    hosts = '127.0.0.1'
    port = 9200
    user = 'elastic' # es用户名
    password = 'KP*rb=PlOgQejHaYIB0P'  # es密码
    index_name = 'my_scrapy_index'  # 索引名称

    # 创建ElasticsearchTool实例并连接Elasticsearch
    es_tool = ElasticsearchTool(hosts, port, user, password, index_name)
    es_tool.connect()

    # 准备批量插入的数据
    # data_list = [
    #     {"id": 1, "text": "这是一个积极的句子", "emotion": "positive"},
    #     {"id": 2, "text": "这是一个消极的句子", "emotion": "negative"},
    #     {"id": 3, "text": "这是一个中性的句子", "emotion": "neutral"}
    # ]

    if data_list:
        for data in data_list:
            # 插入数据
            es_tool.insert_update_doc_by_url(data)

    # # 批量插入数据
    # es_tool.bulk_insert(data_list)
    #
    # # 查询数据
    # query = {
    #     "query": {
    #         "match_all": {}
    #     }
    # }
    # result = es_tool.search(query)
    # if result:
    #     print("查询结果:", result)

    # 关闭连接
    es_tool.close()

def job():
    main()

if __name__ == "__main__":

    # 首次执行
    main()
    # 创建调度器
    scheduler = BlockingScheduler()

    # 每隔10秒执行一次
    # scheduler.add_job(job, IntervalTrigger(seconds=20))
    
    # 每隔30分钟执行一次
    scheduler.add_job(job, IntervalTrigger(minute=30))

    # 每隔1小时执行一次
    # scheduler.add_job(job, IntervalTrigger(hours=1))

    # 每天的10:30执行
    # scheduler.add_job(job, CronTrigger(hour=10, minute=30))

    # 每周一执行
    # scheduler.add_job(job, CronTrigger(day_of_week='mon', hour=0, minute=0))

    # 启动调度器
    scheduler.start()

