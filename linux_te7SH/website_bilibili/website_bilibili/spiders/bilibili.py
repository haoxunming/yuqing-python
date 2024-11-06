import scrapy
import json
import mysql.connector
import jieba

from mysql.connector import Error

from snownlp import SnowNLP
import numpy as np
import urllib.parse
import hashlib
import time
from urllib.parse import quote

from transformers import BertTokenizer, BertForSequenceClassification
import torch
import os

class BilibiliSpider(scrapy.Spider):
    name = "bilibili"
    allowed_domains = ["bilibili.com"]
    start_urls = ["https://bilibili.com"]

    def get_mysql_data(self):
        try:
            mysql_info = self.settings.get('DATABASE')

            keyword_list = []
            data_type = {}
            emotional_data_type = {}
            emotional_type = {}
            # 创建连接
            connection = mysql.connector.connect(
                host=mysql_info['host'],  # 数据库主机地址
                user=mysql_info['user'],  # 数据库用户名
                password=mysql_info['password'],  # 数据库密码
                database=mysql_info['database']  # 数据库名称
            )

            if connection.is_connected():
                db_info = connection.get_server_info()
                print("Connected to MySQL Server version ", db_info)
                # cursor = connection.cursor()
                # 使用 DictCursor 获取字典形式的结果
                cursor = connection.cursor(dictionary=True)
                cursor.execute("select id,programme_name,key_words from t_programme")
                records = cursor.fetchall()
                print("Number of rows in table: ", cursor.rowcount)

                for row in records:
                    if row['key_words']:
                        keywords = row['key_words'].split('、')
                        for keyword in keywords:
                            if keyword and keyword.strip() not in keyword_list:
                                keyword_list.append(keyword.strip())

                cursor.execute("select id,label,value from t_dict_data where dict_type = 'crawler_platform'")
                records = cursor.fetchall()
                for row in records:
                    if row['label'] not in data_type:
                        data_type[row['label']] = row['value']
                if data_type:
                    self.data_type = data_type

                cursor.execute("select id,label,value from t_dict_data where dict_type = 'emotional_attribute'")
                records = cursor.fetchall()
                for row in records:
                    if row['label'] not in emotional_data_type:
                        emotional_data_type[row['label']] = row['value']

                if emotional_data_type:
                    self.emotional_data_type = emotional_data_type

                cursor.execute("select id,label,value from t_dict_data where dict_type = 'emotion'")
                records = cursor.fetchall()
                for row in records:
                    if row['label'] not in emotional_type:
                        emotional_type[row['label']] = row['value']

                if emotional_type:
                    self.emotional_type = emotional_type
            return keyword_list
        except Error as e:
            print("Error while connecting to MySQL", e)
        finally:
            if (connection.is_connected()):
                cursor.close()
                connection.close()
                print("MySQL connection is closed")

    def start_requests(self):
        keyword_list = self.get_mysql_data()
        if not keyword_list:
            return None
        self.keywordDictUrl = {}
        self.url = f'https://api.bilibili.com/x/web-interface/wbi/search/type/'
        for keyword in keyword_list:
            for page in range(1, 10):
                # 获取时间戳
                date_time = int(time.time())
                # 获取w_rid值
                w_rid = self.hash_w_rid(page, date_time, keyword)
                # 请求连接
                url = 'https://api.bilibili.com/x/web-interface/wbi/search/type'

                # 3, 42, 48
                dynamic_offset = page * 16

                params = self.search_keyword(page, 42, dynamic_offset, keyword, w_rid, date_time)
                # 构建完整的URL
                full_url = url + '?' + urllib.parse.urlencode(params)
                yield scrapy.Request(url=full_url, callback=self.parse, meta={'keyword': keyword})

    def parse(self, response):
        source = '哔哩哔哩'
        source_platform = self.data_type['哔哩哔哩']
        response_json = response.json()
        data_list = response_json['data']['result']
        for data in data_list:
            author = data['author']  # 作者
            arcurl = data['arcurl']  # 详情链接
            title = data['title']  # 标题
            description = data['description']  # 内容
            tag = data['tag']  # 关键词 ,
            favorites = data['favorites']  # 收藏
            like = data['like']  # 点赞
            pubdate = data['pubdate']  # 发布时间
            pubdate = pubdate * 1000 if pubdate else None

            pulish_region = '暂无'
            reposts_count = 0
            comments_count = 0

            if title and not tag:
                tag = self.cut_word(title)

            # 情感分析
            snowNLP_anay, snowNLP_anay_score = None, None
            if description:
                snowNLP_anay, snowNLP_anay_score = self.get_text_SnowNLP(description)
            # 情感分析
            snowNLP_anay = self.emotional_data_type[snowNLP_anay] if snowNLP_anay else self.emotional_data_type['中性']
            # 情绪类型
            emotion_type = self.emotional_type[snowNLP_anay_score] if snowNLP_anay_score else self.emotional_type['喜悦']

            yield {
                'type_str': '哔哩哔哩',
                'title': title,
                'author': author,
                'keywords': tag,
                'pulish_region': pulish_region,
                'date': pubdate,
                'date_str': str(pubdate) if pubdate else None,
                'content': description,
                'source': source,
                'reposts_count': int(reposts_count) if reposts_count else 0,    # 转发数
                'comments_count': int(comments_count) if comments_count else 0,   # 评论数
                'attitudes_count': int(like) if like else 0,   # 点赞数
                'collects_count': int(favorites) if favorites else 0,  # 收藏数
                'source_platform': source_platform,
                'qriginal_link': arcurl,
                'snowNLP_anay': snowNLP_anay,
                'emotion_type': emotion_type
            }

    def search_keyword(self, page, page_size, dynamic_offset, keyword, w_rid, date_time):
        params = {
            'ategory_id': '',
            'search_type': 'video',
            'ad_resource': 5654,
            '__refresh__': 'true',
            '_extra': '',
            'context': '',
            'page': page,
            'page_size': page_size,
            'pubtime_begin_s': 0,
            'pubtime_end_s': 0,
            'from_source': '',
            'from_spmid': '333.337',
            'platform': 'pc',
            'highlight': 1,
            'single_column': 0,
            'keyword': keyword,
            'qv_id': '98XjVBEK7IxvzuEngtJuvPMq0yWCNx4R',
            'source_tag': 3,
            'gaia_vtoken': '',
            'dynamic_offset': dynamic_offset,
            'web_location': 1430654,
            'w_rid': w_rid,
            'wts': date_time
        }
        return params

    # 获取w_rid值
    def hash_w_rid(slef, page, date_time, keyword):
        # 使用quote函数进行转码
        encoded_text = quote(keyword, safe='')
        # %E9%AB%98%E6%A0%A1
        f = [
            '__refresh__=true',
            '_extra=',
            'ad_resource=5654',
            'category_id=',
            'context=',
            'dynamic_offset=48',
            'from_source=',
            'from_spmid=333.337',
            'gaia_vtoken=',
            'highlight=1',
            f'keyword={encoded_text}',
            f'page={page}',
            'page_size=42',
            'platform=pc',
            'pubtime_begin_s=0',
            'pubtime_end_s=0',
            'qv_id=98XjVBEK7IxvzuEngtJuvPMq0yWCNx4R',
            'search_type=video',
            'single_column=0',
            'source_tag=3',
            'web_location=1430654',
            f'wts={date_time}'
        ]
        y = '&'.join(f)
        string = y + 'ea1db124af3c7062474693fa704f4ff8'
        md5_ = hashlib.md5()
        md5_.update(string.encode('utf-8'))
        w_rid = md5_.hexdigest()
        return w_rid

    def get_text_SnowNLP(self, text):
        # text-分析文本
        # text = "这家餐厅的服务很好，食物也很美味。"
        # 创建 SnowNLP 对象
        s = SnowNLP(text)

        # 获取情感得分
        sentiment_score = s.sentiments

        # 输出得分
        print("情感得分:", sentiment_score)
        scores_result = None

        # 根据得分判断情感倾向
        if sentiment_score >= 0.6:
            scores_result = '正面'
        elif sentiment_score <= 0.4:
            scores_result = '负面'
        else:
            scores_result = '中性'
            
        return scores_result, self.analyze_text(sentiment_score, text)

        # if scores_result == '中性':
            # return scores_result, self.analyze_text(sentiment_score, text)
        # else:
            # return self.predict_sentiment(text), self.analyze_text(sentiment_score, text)

    def predict_sentiment(self, text):
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

    def analyze_text(self, score, text):
        # 根据得分映射到不同的情绪
        emotions = ['恐惧', '喜悦', '愤怒', '惊奇', '悲伤', '赞扬', '厌恶']
        probabilities = [0.0] * len(emotions)

        # 使用关键词检测来辅助判断
        keywords = ['愤怒', '生气', '恼火', '气愤', '霸凌', '欺凌', '糟糕', '失败', '差劲', '痛苦', '悲伤', '失望',
                    '不幸', '糟糕透顶', '困难', '艰难', '困惑', '沮丧', '绝望', '糟糕的', '失败的', '不好的',
                    '恶劣', '糟糕极了', '令人失望', '悲惨', '灾难', '糟糕情况', '糟糕经历',
                    '糟糕体验', '悲痛', '痛苦经历', '痛苦体验', '令人痛苦', '糟糕结果']
        has_anger_keyword = any(keyword in text for keyword in keywords)

        if has_anger_keyword:
            probabilities[emotions.index('愤怒')] = 0.9
            probabilities[emotions.index('悲伤')] = 0.1
        else:
            if score > 0.8:
                probabilities[emotions.index('喜悦')] = 0.9
                probabilities[emotions.index('赞扬')] = 0.1
            elif score > 0.6:
                probabilities[emotions.index('喜悦')] = 0.7
                probabilities[emotions.index('赞扬')] = 0.3
            elif score > 0.4:
                probabilities[emotions.index('喜悦')] = 0.5
                probabilities[emotions.index('赞扬')] = 0.5
            elif score > 0.2:
                probabilities[emotions.index('喜悦')] = 0.3
                probabilities[emotions.index('赞扬')] = 0.7
            elif score > 0.0:
                probabilities[emotions.index('喜悦')] = 0.1
                probabilities[emotions.index('赞扬')] = 0.9
            elif score < 0.2:
                probabilities[emotions.index('悲伤')] = 0.9
                probabilities[emotions.index('厌恶')] = 0.1
            elif score < 0.4:
                probabilities[emotions.index('悲伤')] = 0.7
                probabilities[emotions.index('厌恶')] = 0.3
            elif score < 0.6:
                probabilities[emotions.index('悲伤')] = 0.5
                probabilities[emotions.index('厌恶')] = 0.5
            elif score < 0.8:
                probabilities[emotions.index('悲伤')] = 0.3
                probabilities[emotions.index('厌恶')] = 0.7
            else:
                probabilities[emotions.index('悲伤')] = 0.1
                probabilities[emotions.index('厌恶')] = 0.9

        # 输出每种情绪的概率
        for i, emotion in enumerate(emotions):
            print(f'{emotion}: {probabilities[i]:.2f}')

        # 最可能的情绪
        predicted_emotion = emotions[np.argmax(probabilities)]
        print(f'预测的情绪: {predicted_emotion}')
        return predicted_emotion

    def cut_word(self, text):
        # 精确模式
        seg_list = jieba.cut(text, cut_all=False)
        seg_list_word = []
        for item in seg_list:
            if len(item) > 1:
                seg_list_word.append(item)

        return ";".join(seg_list_word)
