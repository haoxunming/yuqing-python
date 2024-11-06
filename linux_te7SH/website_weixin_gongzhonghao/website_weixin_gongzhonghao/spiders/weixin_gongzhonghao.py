import scrapy
import urllib.parse
import json

import json
import mysql.connector
import jieba

from mysql.connector import Error

from snownlp import SnowNLP
import numpy as np

from transformers import BertTokenizer, BertForSequenceClassification
import torch
import os

class WeixinGongzhonghaoSpider(scrapy.Spider):
    name = 'weixin_gongzhonghao'
    # allowed_domains = ['weixin.com']
    # start_urls = ['http://weixin.com/']

    def get_mysql_data(self):
        try:
            mysql_info = self.settings.get('DATABASE')

            self.taken_val = self.settings.get('WEIXING_TAKEN')

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
        for keyword in keyword_list:
            offset, count = 0, 5
            # 请求连接
            url = 'https://mp.weixin.qq.com/cgi-bin/searchbiz'
            params = self.search_gongzhonghao(offset, count, keyword)
            # 构建完整的URL
            full_url = url + '?' + urllib.parse.urlencode(params)
            yield scrapy.Request(url=full_url, callback=self.parse, meta={'keyword': keyword})

    def parse(self, response):
        keyword = response.meta['keyword']
        response_json = response.json()
        data_list = response_json['list']
        url_detail = 'https://mp.weixin.qq.com/cgi-bin/appmsgpublish'

        # full_url = 'https://mp.weixin.qq.com/cgi-bin/appmsgpublish?sub=search&search_field=7&begin=0&count=5&query=%E9%AB%98%E6%A0%A1&fakeid=MzkwMzE2MzQyMQ%3D%3D&type=101_1&free_publish_type=1&sub_action=list_ex&token=682955046&lang=zh_CN&f=json&ajax=1'
        # yield scrapy.Request(url=full_url, callback=self.parse_detail123, meta={'nickname': '123'})
        # try:
        #     yield scrapy.Request(url=full_url, callback=self.parse_detail123, meta={'nickname': '123'})
        # except Exception as e:
        #     print(f"请求 {full_url} 失败: {e}")
        for data in data_list:
            fakeid = data['fakeid']
            nickname = data['nickname']
            offset, count = 0, 5
            params = self.search_gongzhonghao_detail(offset, count, keyword, fakeid)
            # 构建完整的URL
            full_url = url_detail + '?' + urllib.parse.urlencode(params)
            print(full_url)
            yield scrapy.Request(url=full_url, callback=self.parse_detail123, meta={'nickname': nickname})

    def parse_detail123(self, response):
        nickname = response.meta['nickname']
        response_detail = response.json()
        publish_page = json.loads(response_detail['publish_page'])
        publish_list = publish_page['publish_list']
        for publish_obj in publish_list:
            publish_info = json.loads(publish_obj['publish_info'])
            result_list = publish_info['appmsgex']
            for result_obj in result_list:
                print(f'==============================================================')
                title = result_obj['title']
                link = result_obj['link']
                # digest = result_obj['digest']
                create_time = result_obj['create_time']

                yield scrapy.Request(url=link, callback=self.parse_detail_bylink, meta={'title': title, 'nickname': nickname, 'create_time': create_time})

    def parse_detail_bylink(self, response):
        source = '微信公众号'
        source_platform = self.data_type['微信公众号']
        qriginal_link = response.url
        title = response.meta['title']  # 标题
        nickname = response.meta['nickname']  # 作者
        publish_time = response.meta['create_time']  # 发布时间
        publish_time = publish_time * 1000 if publish_time else None

        # publish_time = response.css('div#meta_content span#meta_content_hide_info em#publish_time::text').get()
        pulish_region = response.css('div#meta_content span#meta_content_hide_info em#js_ip_wording_wrp span#js_ip_wording::text').get()
        # 使用 CSS 选择器获取 id='js_content' 的 div 下的所有 <p> 标签内的 <span> 标签的文本
        list_data = response.css('#js_content p span::text').getall()

        content = ''.join(list_data)

        if not title:
            title = response.css('div.rich_media_wrp h1#activity-name::text').get()

        if title:
            keywords = self.cut_word(title)

        reposts_count = 0
        comments_count = 0
        attitudes_count = 0
        collects_count = 0

        # 情感分析
        snowNLP_anay, snowNLP_anay_score = None, None
        if content:
            snowNLP_anay, snowNLP_anay_score = self.get_text_SnowNLP(content)
        # 情感分析
        snowNLP_anay = self.emotional_data_type[snowNLP_anay] if snowNLP_anay else self.emotional_data_type['中性']
        # 情绪类型
        emotion_type = self.emotional_type[snowNLP_anay_score] if snowNLP_anay_score else self.emotional_type['喜悦']

        yield {
            'type_str': '微信公众号',
            'title': title,
            'author': nickname,
            'keywords': keywords,
            'pulish_region': pulish_region,
            'date': publish_time,
            'date_str': str(publish_time) if publish_time else None,
            'content': content,
            'source': source,
            'reposts_count': int(reposts_count) if reposts_count else 0,
            'comments_count': int(comments_count) if comments_count else 0,
            'attitudes_count': int(attitudes_count) if attitudes_count else 0,
            'collects_count': int(collects_count) if collects_count else 0,
            'source_platform': source_platform,
            'qriginal_link': qriginal_link,
            'snowNLP_anay': snowNLP_anay,
            'emotion_type': emotion_type
        }

    # 根据关键词搜索公众号
    def search_gongzhonghao(self, offset, count, keyword):
        params = {
            'action': 'search_biz',
            'begin': offset,
            'count': count,
            'query': f'{keyword}',
            'token': self.taken_val,
            'lang': 'zh_CN',
            'f': 'json',
            'ajax': '1'
        }

        return params

    def search_gongzhonghao_detail(self, offset, count, keyword, fakeid):
        params_deail = {
            'sub': 'search',  # search 代表搜索, list 代表列表(没有检索词)
            'search_field': '7',  # 当sub 为 list 时，此参数为null, 当sub 为 search 时，此参数为7,
            'begin': offset,
            'count': count,
            'query': keyword,  # 搜索内容  ； 当sub 为 list 时，此参数为空
            'fakeid': fakeid,
            'type': '101_1',
            'free_publish_type': 1,
            'sub_action': 'list_ex',
            'token': self.taken_val,
            'lang': 'zh_CN',
            'f': 'json',
            'ajax': '1'
        }

        return params_deail

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
