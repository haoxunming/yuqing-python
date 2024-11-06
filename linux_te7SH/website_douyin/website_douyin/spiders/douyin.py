import scrapy
import json
import mysql.connector
import jieba

from mysql.connector import Error

from snownlp import SnowNLP
import numpy as np
import urllib.parse

from transformers import BertTokenizer, BertForSequenceClassification
import torch
import os

class DouyinSpider(scrapy.Spider):
    name = "douyin"
    allowed_domains = ["douyin.com"]
    start_urls = ["https://douyin.com"]

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
        self.url = f'https://www.douyin.com/aweme/v1/web/search/item/'
        for keyword in keyword_list:
            offset = 0
            count = 16
            params = self.search_keyword(keyword, offset, count)
            # 构建完整的URL
            full_url = self.url + '?' + urllib.parse.urlencode(params)
            yield scrapy.Request(url=full_url, callback=self.parse, meta={'keyword': keyword, 'offset': offset, 'count': count})

    def parse(self, response):
        obje_dict = {}
        keyword = response.meta['keyword']
        offset = response.meta['offset']
        count = response.meta['count']
        json_data = json.loads(response.text)

        obje_dict['keyword'] = keyword
        obje_dict['offset'] = offset
        obje_dict['count'] = count
        obje_dict['json_data'] = json_data

        self.keywordDictUrl[keyword] = obje_dict

        for video_data in json_data['data']:
            video_data_obj = self.save_video_info(video_data['aweme_info'], keyword)
            yield video_data_obj

        if self.keywordDictUrl[keyword]['json_data']['has_more'] == 0:
            return
        else:
            offset = self.keywordDictUrl[keyword]['offset'] + self.keywordDictUrl[keyword]['count']
            if offset < 50:
                count = 16
                params = self.search_keyword(keyword, offset, count)
                # 构建完整的URL
                full_url = self.url + '?' + urllib.parse.urlencode(params)
                yield scrapy.Request(url=full_url, callback=self.parse, meta={'keyword': keyword, 'offset': offset, 'count': count})

    def search_keyword(self, keyword, offset, count):
        params = {
            'aid': '6383',
            'channel': 'channel_pc_web',
            'search_channel': 'aweme_video_web',
            'keyword': keyword,
            'offset': offset,
            'publish_time': 7,  # 筛选时间：0：全部，1：今天，7：7天内，30：30天内  182: 6个月内
            'sort_type': 2,  # 排序类型：0：默认(综合排序)，1：最多点赞，2：最新发布
            'is_filter_search': 1,  # 是否筛选 ： 0：否，1：是
            'count': count
        }

        return params

    def save_video_info(self, video_data, keywordField):
        # 来源平台
        source_platform = self.data_type['抖音']

        minutes = video_data['video']['duration'] // 1000 // 60
        seconds = video_data['video']['duration'] // 1000 % 60

        # 标题
        title = video_data['desc']
        # 作者
        author = video_data['author']['nickname']
        # 关键词
        keywords = None
        if title:
            keywords = self.cut_word(title)
        # 发布地
        pulish_region = '暂无'
        # 发表时间
        date = int(video_data['create_time']) * 1000 if video_data['create_time'] else 0
        # 视频描述
        content = video_data['desc']
        # 视频链接
        video_url = video_data['video']['play_addr']['url_list'][0]
        # 详情链接
        # qriginal_link = f'https://www.douyin.com/search/{keywordField}?modal_id={video_data["aweme_id"]}&type=video'
        qriginal_link = f'https://www.douyin.com/video/{video_data["aweme_id"]}'
        # 来源
        source = video_data['author']['nickname']
        # 转发数
        reposts_count = video_data['statistics']['forward_count']
        # 评论数
        comments_count = video_data['statistics']['comment_count']
        # 点赞数
        attitudes_count = video_data['statistics']['digg_count']
        # 收藏数
        collects_count = video_data['statistics']['collect_count']
        # 粉丝数量
        follower_count = video_data['author']['follower_count']
        # 下载数量
        download_count = video_data['statistics']['download_count']
        # 分享数量
        share_count = video_data['statistics']['share_count']

        # 情感分析
        snowNLP_anay, snowNLP_anay_score = None, None
        if content:
            snowNLP_anay, snowNLP_anay_score = self.get_text_SnowNLP(content)
        # 情感分析
        snowNLP_anay = self.emotional_data_type[snowNLP_anay] if snowNLP_anay else self.emotional_data_type['中性']
        # 情绪类型
        emotion_type = self.emotional_type[snowNLP_anay_score] if snowNLP_anay_score else self.emotional_type['喜悦']


        # video_dict = {
        #     '用户名': video_data['author']['nickname'],
        #     '粉丝数量': video_data['author']['follower_count'],
        #     '发表时间': video_data['create_time'],
        #     '视频描述': video_data['desc'],
        #     '点赞数量': video_data['statistics']['digg_count'],
        #     '收藏数量': video_data['statistics']['collect_count'],
        #     '评论数量': video_data['statistics']['comment_count'],
        #     '下载数量': video_data['statistics']['download_count'],
        #     '分享数量': video_data['statistics']['share_count'],
        #     '转发数量': video_data['statistics']['forward_count'],
        #  }

        video_dict = {
            'type_str': '抖音',
            'title': title,
            'author': author,
            'keywords': keywords,
            'pulish_region': pulish_region,
            'date': date,
            'date_str': str(date) if date else None,
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

        return video_dict

        # 使用 Python 进行中文文本的情感分析，可以使用专门针对中文设计的库，如 SnowNLP。SnowNLP 是一个简单易用的中文文本处理库，支持中文分词、情感分析等功能
        # 安装 SnowNLP
        # 首先确保安装了 SnowNLP 库。pip install snownlp
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
