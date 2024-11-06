from elasticsearch import Elasticsearch
import re
from settings import ELASTICSEARCH_DATABASE

# 连接到 Elasticsearch
# es = Elasticsearch([{"host": "47.94.246.151", "port": 9200, "scheme": "https"}])
# 连接到 Elasticsearch，禁用 SSL 证书验证
# es = Elasticsearch([{"host": "47.94.246.151", "port": 9200, "scheme": "https"}], verify_certs=False)

es_info = ELASTICSEARCH_DATABASE

# 连接到 Elasticsearch，提供用户名和密码
# es = Elasticsearch([{"host": "47.94.246.151", "port": 9200, "scheme": "https"}], http_auth=("elastic", "+3*cj2yW=oyZBlfcpFVb"), verify_certs=False)
es = Elasticsearch([{"host": es_info['host'], "port": es_info['port'], "scheme": "https"}], http_auth=(es_info['user'], es_info['password']), verify_certs=False)

index_name = es_info['database']
# 检查索引是否存在
if not es.indices.exists(index=index_name):
    # 如果索引不存在，则创建索引
    es.indices.create(index=index_name, body={
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
# 定义索引名称
# index_name = "my_scrapy_index"
# index_name = es_info['database']


# 新增函数：插入新文档
def insert_new_doc(dict_data):
    """
    向Elasticsearch索引中插入一条新的文档。

    :param dict_data: 包含文档数据的字典
    """
    try:
        # 插入文档
        es.index(index=index_name, document=dict_data)
        print(f"文档插入成功: {dict_data}")
    except Exception as e:
        print(f"插入文档时发生错误: {e}")

# 根据url,修改文档
def update_doc_by_url(dict_data):
    # 定义查询条件（无查询条件），匹配所有文档
    # query_body = {
    #     "query": {
    #         "match_all": {}
    #     }
    # }

    # 定义查询条件，通过 url 字段找到特定文档
    query_body = {
        "query": {
            "term": {
                "qriginal_link.keyword": dict_data['qriginal_link']
            }
        }
    }

    # 执行搜索操作，获取所有文档
    response = es.search(index=index_name, body=query_body, size=10000)

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
        es.update(index=index_name, id=hit['_id'], body=update_body)
    print("更新完成")

def insert_update_doc_by_url(dict_data):
    # 定义查询条件，通过 url 字段找到特定文档
    query_body = {
        "query": {
            "term": {
                "qriginal_link.keyword": dict_data['qriginal_link']
            }
        }
    }

    # 执行搜索操作，获取所有文档
    response = es.search(index=index_name, body=query_body, size=10000)

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
            es.update(index=index_name, id=hit['_id'], body=update_body)
        print("更新完成")
    else:
        # 新增
        try:
            # 插入文档
            es.index(index=index_name, document=dict_data)
            print(f"文档插入成功: {dict_data}")
        except Exception as e:
            print(f"插入文档时发生错误: {e}")

# 删除所有 date_str 为 null 的文档
def delete_doc_by_():
    # 定义查询条件，查找 date_str 为 null 的文档
    query_body = {
        "query": {
            "bool": {
                "must_not": [
                    {"exists": {"field": "date_str"}}
                ]
            }
        }
    }

    # 执行搜索操作，获取所有 date_str 为 null 的文档
    response = es.search(index=index_name, body=query_body, size=10000)

    # 删除文档
    for hit in response['hits']['hits']:
        # 获取文档 ID
        doc_id = hit['_id']

        # 执行删除操作
        es.delete(index=index_name, id=doc_id)

    print("删除完成")








