from urllib.parse import urlparse
import sys
import scrapy
import json
import re
import jieba
from datetime import datetime
from scrapy import FormRequest
from website_weibo.items import WeiboItem
import numpy as np

# sys.path += ['./', '../']  # allow 'shared' to be imported below
# import shared.common as c
# import shared.config as config
# from shared.mysql_helper import use_mysql

import mysql.connector
from mysql.connector import Error

from transformers import BertTokenizer, BertForSequenceClassification
import torch
import os


class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    allowed_domains = ['weibo.com']
    # start_urls = ['https://s.weibo.com/weibo?q={}'.format('python')]
    # start_urls = ['http://httpbin.org/get']

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
    # def get_mysql_data(self):
    #     keyword_list = []
    #     data_type = {}
    #     emotional_data_type = {}
    #     with use_mysql(None, config.get_mysql_config(profile='wesite_collection', database='public_sentiment'), unbuff_cur=False, err=(err := c.EntityThrow())) as cur:
    #         if not err.hasex:
    #             stmt = f'select id,programme_name,key_words from t_programme'
    #             cur.execute(stmt)
    #             for r in cur:
    #                 r = c.EntityThrow(r)
    #                 if r.key_words:
    #                     keywords = r.key_words.split('+')
    #                     for keyword in keywords:
    #                         if keyword and keyword.strip() not in keyword_list:
    #                             keyword_list.append(keyword.strip())
    #             stmt = f"select id,label,value from t_dict_data where dict_type = 'crawler_platform'"
    #             cur.execute(stmt)
    #             for r in cur:
    #                 r = c.EntityThrow(r)
    #                 if r.label not in data_type:
    #                     data_type[r.label] = r.value
    #
    #             stmt = f"select id,label,value from t_dict_data where dict_type = 'emotional_attribute'"
    #             cur.execute(stmt)
    #             for r in cur:
    #                 r = c.EntityThrow(r)
    #                 if r.label not in emotional_data_type:
    #                     emotional_data_type[r.label] = r.value
    #
    #             if emotional_data_type:
    #                 self.emotional_data_type = emotional_data_type
    #     return keyword_list, data_type, emotional_data_type

    def start_requests(self):
        keyword_list = self.get_mysql_data()
        if not keyword_list:
            return None
        # keyword_list = ['美国', '特朗普']
        self.exit_link_list = []
        for keyword in keyword_list:
            url = 'https://s.weibo.com/weibo?q={}'.format(keyword)
            # yield FormRequest(url, callback=self.parse)
            # yield scrapy.Request(url, callback=self.parse, meta={'source_platform': data_type['微博']})
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        print(f'######################################{response.url}########################################')
        # source_platform = response.meta.get('source_platform')
        #获取所有具有mid属性的div.card-wrap元素
        card_wraps = response.css('div.woo-box-flex div.main-full div.card-wrap[mid]')
        for card_wrap in card_wraps:
            bozhu_link = card_wrap.css('div.card div.content div.info > div:nth-child(2) >  a::attr(href)').get()
            detail_lin = card_wrap.css('div.card div.content div.from a::attr(href)').get()
            # yield scrapy.Request(url=response.urljoin(detail_lin), callback=self.parse_deatail_obj, meta={'source_platform': source_platform})
            yield scrapy.Request(url=response.urljoin(detail_lin), callback=self.parse_deatail_obj)

        # last_li = response.css('div.m-page div span.list ul li:last-child')
        last_li = response.css('div.m-page div span.list ul li')
        page_list = len(last_li)
        link_url_page = response.url
        new_url = re.sub(r'&page=\d+', '', link_url_page)

        # 如果超过10页，则10为阈值
        page_list = 5 if page_list > 5 else page_list

        if new_url not in self.exit_link_list and page_list > 1:
            self.exit_link_list.append(response.url)
            for i in range(2, page_list + 1):
                url = '{}&page={}'.format(response.url, i)
                print(f'========================{url}================================')
                #yield scrapy.Request(url, callback=self.parse, meta={'source_platform': source_platform})
                yield scrapy.Request(url, callback=self.parse)

    def parse_deatail_obj(self, response):
        # source_platform = response.meta.get('source_platform')
        #获取所有具有mid属性的div.card-wrap元素
        request_url = response.url
        # 使用 urlparse 解析 URL
        parsed_url = urlparse(request_url)
        # 获取id
        path_str = parsed_url.path
        # 获取最后一个斜杠 '/' 之后的内容
        last_slash_index = path_str.rfind('/')
        detail_id = path_str[last_slash_index + 1:]
        detail_url = 'https://weibo.com/ajax/statuses/longtext?id={}'.format(detail_id)
        # yield scrapy.Request(url=detail_url, callback=self.parse_detail_longtext, meta={'detail_url_id': detail_id, 'link_url': response.urljoin(request_url), 'source_platform': source_platform})
        yield scrapy.Request(url=detail_url, callback=self.parse_detail_longtext, meta={'detail_url_id': detail_id, 'link_url': response.urljoin(request_url)})

    def parse_detail_longtext(self, response):
        detail_url_id = response.meta.get('detail_url_id')
        link_url = response.meta.get('link_url')
        # source_platform = response.meta.get('source_platform')
        json_str = response.text
        try:
            if json_str:
                # 将JSON字符串转换为Python字典
                json_data = json.loads(json_str)
                data_meta = json_data['data']
                if data_meta:
                    long_text = data_meta['longTextContent']
                else:
                    long_text = None
                detail_url = 'https://weibo.com/ajax/statuses/show?id={}&locale=zh-CN'.format(detail_url_id)
                # yield scrapy.Request(url=detail_url, callback=self.parse_detail_index, meta={'long_text': long_text, 'link_url': link_url, 'source_platform': source_platform})
                yield scrapy.Request(url=detail_url, callback=self.parse_detail_index, meta={'long_text': long_text, 'link_url': link_url})

        except json.JSONDecodeError:
            # 处理解析JSON时可能出现的错误
            self.logger.error('解析JSON时出错: {}'.format(response.url))

    def parse_detail_index(self, response):
        json_str = response.text
        long_text = response.meta.get('long_text')
        link_url = response.meta.get('link_url')
        # 来源平台
        # source_platform = response.meta.get('source_platform')
        source_platform = self.data_type['微博']
        try:
            if json_str:
                # 将JSON字符串转换为Python字典
                json_data = json.loads(json_str)
                # 博主
                author = json_data['user']['screen_name']
                # 标题
                title = json_data['topic_struct'][0]['topic_title'] if 'topic_struct' in json_data and len(json_data['topic_struct']) > 0 and 'topic_title' in json_data['topic_struct'][0] else ''
                # 发布地
                pulish_region = json_data['region_name'] if 'region_name' in json_data else ''
                # 发布时间
                publish_time = json_data['created_at']
                # 解析原始日期字符串
                date_obj = datetime.strptime(publish_time, "%a %b %d %H:%M:%S %z %Y")
                # 格式化日期
                publish_time = date_obj.strftime("%Y年%m月%d日 %H:%M:%S")
                publish_time = datetime.strptime(publish_time, "%Y年%m月%d日 %H:%M:%S") if publish_time else None
                date = publish_time.timestamp() * 1000 if publish_time else None

                keywords = self.cut_word(title) if title else None
                # 内容
                content = long_text if long_text else json_data['text_raw']
                if not title and content:
                    title = content[:10] if len(content) > 10 else content
                    keywords = self.cut_word(content)
                # 情感分析
                if content:
                    snowNLP_anay, snowNLP_anay_score = self.get_text_SnowNLP(content)
                # 情感分析
                snowNLP_anay = self.emotional_data_type[snowNLP_anay] if snowNLP_anay else self.emotional_data_type['中性']
                # 情绪类型
                emotion_type = self.emotional_type[snowNLP_anay_score] if snowNLP_anay_score else self.emotional_type['喜悦']
                # 来源
                source = json_data['source']
                # 转发数
                reposts_count = json_data['reposts_count']
                # 评论数
                comments_count = json_data['comments_count']
                # 点赞数
                attitudes_count = json_data['attitudes_count']
                # 收藏数 微博暂无收藏数
                collects_count = 0
                # 原文链接
                link_url = link_url
                yield WeiboItem(
                    type_str='微博',
                    title=title,
                    author=author,
                    keywords=keywords,
                    pulish_region=pulish_region,
                    date=date,
                    date_str=str(date) if date else None,
                    content=content,
                    source=source,
                    reposts_count=reposts_count,
                    comments_count=comments_count,
                    attitudes_count=attitudes_count,
                    collects_count=collects_count,
                    source_platform=source_platform,
                    qriginal_link=link_url,
                    snowNLP_anay=snowNLP_anay,
                    emotion_type=emotion_type)

        except json.JSONDecodeError:
            # 处理解析JSON时可能出现的错误
            self.logger.error('解析JSON时出错: {}'.format(response.url))

    # 使用 Python 进行中文文本的情感分析，可以使用专门针对中文设计的库，如 SnowNLP。SnowNLP 是一个简单易用的中文文本处理库，支持中文分词、情感分析等功能
    # 安装 SnowNLP
    # 首先确保安装了 SnowNLP 库。pip install snownlp
    def get_text_SnowNLP(self, text):
        from snownlp import SnowNLP

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

if __name__ == '__main__':
    text = "（记者 彭晨阳）9月12日，中国石油启动2024年秋季高校毕业生招聘。本次招聘主要面向2025届高校毕业生，以及符合报名条件并取得国家教育部留学服务中心学历学位认证的留学回国人员；未落实工作单建设目标，统筹考虑队伍结构优化及核心业务、新兴产业、未来产业等重点领域人才补充，扩大高校毕业生招聘规模，优化学历结构和专业投向，重点面向“双碳三新”、生物化工、数理化、人工智能和大数据及石油石化等主体责任担当。 　　本次招聘报名于2024年10月30日截止。中国石油高校毕业生招聘平台（https://zhaopin.cnpc.com.cn）是此次毕业生招聘的唯一渠道，无其他报名方式，具体招聘岗位及招聘条件可登录网站查询。"
    weibo_spider = WeiboSpider()
    result = weibo_spider.predict_sentiment(text)
    print(f"输入文本: {text}")
    print(f"情感分析结果: {result}")

