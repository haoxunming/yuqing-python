import scrapy
import json
from datetime import datetime
import jieba

import mysql.connector
from mysql.connector import Error
import numpy as np

from transformers import BertTokenizer, BertForSequenceClassification
import torch
import os

class WangyiSpider(scrapy.Spider):
    name = "wangyi"
    allowed_domains = ["163.com"]
    # start_urls = ["https://news.163.com"]

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
        # keyword_list = ['美国']
        self.keyword_page_num = {}
        for keyword in keyword_list:
            url = 'https://www.163.com/search?keyword={}'.format(keyword)
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        print(f'######################################{response.url}########################################')
        # 获取所有具有mid属性的div.card-wrap元素
        card_wraps = response.css('div.keyword_list div.keyword_new h3 a::attr(href)').getall()
        for detail_lin in card_wraps:
            if 'v/video' not in detail_lin:
                yield scrapy.Request(url=response.urljoin(detail_lin), callback=self.parse_china_detail)

    def parse_china_detail(self, response):
        # 采集网站名称
        source_platform = self.data_type['网易']
        # 解析世界新闻列表页，提取新闻链接
        #用css选择器获取class=post_main的div下的class=post_title的h1标签的页。
        # 标题
        title = response.css('div.post_main h1.post_title::text').get()

        snowNLP_anay, snowNLP_anay_score = '中性', '喜悦'

        # 作者
        author = response.css('.creative_statement::text').get()
        if not author:
            author = response.css('div.post_main div.post_content div.post_author::text').getall()
            index_num = author[1].find('责任编辑') if author and len(author) > 1 and '责任编辑' in author[1] else 0
            author = author[1][index_num:].replace('\n', '').strip() if index_num > 0 else ''
        # 发布日期
        # 注意：strip=True用于去除文本前后的空白符
        # date = response.css('.date-source .date::text').get(strip=True)
        date_format = "%Y-%m-%d %H:%M:%S"
        date_string = response.css('div.post_main div.post_info::text').get()
        date_string = date_string.strip() if date_string else ''
        if date_string:
            date_string = date_string.strip()
            date_string = date_string.replace('\n', '')[:-4].strip()
            dt = datetime.strptime(date_string, date_format)
            date = dt.timestamp() * 1000
        else:
            date = 0
        # 内容
        content = '\n'.join(response.css('div.post_content div.post_body p::text').extract())

        # 情感分析
        if content:
            snowNLP_anay, snowNLP_anay_score = self.get_text_SnowNLP(content)
        # 情感分析
        snowNLP_anay = self.emotional_data_type[snowNLP_anay] if snowNLP_anay else self.emotional_data_type['中性']
        # 情绪类型
        emotion_type = self.emotional_type[snowNLP_anay_score] if snowNLP_anay_score else self.emotional_type['喜悦']

        # 关键词
        keywords = None
        if title:
            keywords = self.cut_word(title)
        # 发布来源
        source = response.css('div.post_main div.post_info a::text').get()

        # 发布地区
        pulish_region = '未知'
        data_pub_list = response.css('div.post_info ::text').getall()
        if data_pub_list and len(data_pub_list) > 3:
            pulish_region = data_pub_list[3].replace('\n', '').strip()
        # 参与人数
        # if not comments_num:
        #     comments_num = response.css('.sina-comment-top .clearfix span em a::text').get()
        comments_num = 0
        # 原文链接
        qriginal_link = response.url
        if qriginal_link:
            yield {
                'type_str': '网易',
                'title': title,
                'author': author,
                'keywords': keywords,
                'pulish_region': pulish_region,
                'date': date,
                'date_str': str(date),
                'content': content,
                'source': source,
                'reposts_count': 0,
                'comments_count': int(comments_num) if comments_num else 0,
                'attitudes_count': 0,
                'collects_count': 0,
                'source_platform': source_platform,
                'qriginal_link': qriginal_link,
                'snowNLP_anay': snowNLP_anay,
                'emotion_type': emotion_type
            }

    # def parse(self, response):
    #     navigation_bar_list = response.xpath('//div[@class="index_head"]/div[@class="bd"]/div[contains(@class, "ns_area")]//a')
    #     naviga_bar_links = {}
    #     for bar_obj in navigation_bar_list:
    #         bar_obj_text = bar_obj.xpath('./text()').get()
    #         bar_obj_href = bar_obj.xpath('./@href').get()
    #         if bar_obj_text == '国内' or bar_obj_text == '国际':
    #             naviga_bar_links[bar_obj_text] = bar_obj_href
    #         else:
    #             continue
    #
    #     for text in naviga_bar_links.keys():
    #         yield scrapy.Request(url=naviga_bar_links[text], callback=self.parse_news, meta={'model': text})

    # def parse_news(self, response):
    #     if response.meta['model'] == '国内':
    #         info_url = 'https://news.163.com/special/cm_guonei/?callback=data_callback'
    #         yield scrapy.Request(url=info_url, callback=self.parse_china, meta={'type_str': response.meta['model'], 'page_num': 1})

    # def parse_china(self, response):
    #     type_str = response.meta.get('type_str')
    #     page_num = response.meta.get('page_num')
    #     json_str = response.text
    #     try:
    #         if json_str:
    #             # 去除字符串前后空格
    #             json_str = json_str.strip()
    #             # 替换字符串中的换行符
    #             json_str = json_str.replace('\n', '')
    #             # 切割字符串
    #             json_str = json_str[14:-1]
    #             # 将JSON字符串转换为Python字典
    #             json_data = json.loads(json_str)
    #
    #             if json_data:
    #                 self.current_page_items_count = len(json_data)
    #
    #             if json_data and len(json_data) > 0:
    #                 for item in json_data:
    #                     # 获取关键词
    #                     keywords = item['keywords']
    #                     keywords_list = []
    #                     if keywords:
    #                         for keywords_item in keywords:
    #                             keywords_list.append(keywords_item['keyname'])
    #                     if keywords_list:
    #                         keywords_str = ';'.join(keywords_list)
    #                     else:
    #                         keywords_str = None
    #
    #                     # 获取来源
    #                     source = item['source'] if item['source'] else None
    #
    #                     # 获取参与人数
    #                     comments_num = item['tienum'] if item['tienum'] else None
    #                     # 在这里处理每个数据项
    #                     yield scrapy.Request(url=item['docurl'], callback=self.parse_china_detail, meta={'type_str': type_str, 'keywords_str': keywords_str, 'source': source, 'comments_num': comments_num})
    #
    #             if hasattr(self, 'current_page_items_count'):
    #                 if not self.current_page_items_count or self.current_page_items_count == 0:
    #                     return
    #             info_url = 'https://news.163.com/special/cm_guonei_0{}/?callback=data_callback'
    #             urls = info_url.format(page_num + 1)
    #             yield scrapy.Request(url=urls, callback=self.parse_china, errback=self.handle_error, meta={'type_str': type_str, 'page_num': page_num + 1})
    #         # 现在你可以像处理普通Python字典一样处理json_data了
    #         # 例如，打印某个键的值
    #         # print(json_data['title'])
    #
    #         # 你可以在这里进一步处理数据，比如生成Item对象
    #         # ...
    #
    #     except json.JSONDecodeError:
    #         # 处理解析JSON时可能出现的错误
    #         self.logger.error('解析JSON时出错: {}'.format(response.url))

    def handle_error(self, failure):
        code = failure.value.response.status
        if code == 404:
            self.current_page_items_count = 0
        # 在这里处理错误
        self.logger.error(failure)

    # def parse_china_detail(self, response):
    #     # 采集网站名称
    #     type_str = response.meta.get('type_str')
    #     # 关键词
    #     keywords_str = response.meta.get('keywords_str')
    #     # 来源
    #     source = response.meta.get('source')
    #     # 参与人数
    #     comments_num = response.meta.get('comments_num')
    #     # 解析世界新闻列表页，提取新闻链接
    #     #用css选择器获取class=post_main的div下的class=post_title的h1标签的页。
    #     # 标题
    #     title = response.css('div.post_main h1.post_title::text').get()
    #     # 情感分析
    #     snowNLP_anay = self.get_text_SnowNLP(title)
    #     # 作者
    #     author = response.css('.creative_statement::text').get()
    #     if not author:
    #         author = response.css('div.post_main div.post_content div.post_author::text').getall()
    #         index_num = author[1].find('责任编辑')
    #         author = author[1][index_num:].replace('\n', '').strip()
    #     # 发布日期
    #     # 注意：strip=True用于去除文本前后的空白符
    #     # date = response.css('.date-source .date::text').get(strip=True)
    #     date_format = "%Y-%m-%d %H:%M:%S"
    #     date_string = response.css('div.post_main div.post_info::text').get().strip()
    #     date_string = date_string.replace('\n', '')[:-4].strip()
    #     dt = datetime.strptime(date_string, date_format)
    #     date = dt.timestamp() * 1000
    #     # 内容
    #     content = '\n'.join(response.css('div.post_content div.post_body p::text').extract())
    #     # 关键词
    #     if keywords_str:
    #         keywords = keywords_str
    #     if not keywords_str:
    #         keywords = self.cut_word(title)
    #     # 发布来源
    #     if not source:
    #         source = response.css('div.post_main div.post_info a::text').get()
    #     # 参与人数
    #     # if not comments_num:
    #     #     comments_num = response.css('.sina-comment-top .clearfix span em a::text').get()
    #     # 原文链接
    #     qriginal_link = response.url
    #     if qriginal_link:
    #         yield {
    #             'type_str': type_str,
    #             'title': title,
    #             'snowNLP_anay': snowNLP_anay,
    #             'author': author,
    #             'date': date,
    #             'date_str': str(date),
    #             'content': content,
    #             'comments_num': int(comments_num) if comments_num else 0,
    #             'keywords': keywords,
    #             'qriginal_link': qriginal_link,
    #             'source': source,
    #             'source_platform': 2
    #         }

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

        # 全模式
        # seg_list = jieba.cut(text, cut_all=True)
        # print("全模式:", " ".join(seg_list))

        # 搜索引擎模式
        # seg_list = jieba.cut_for_search(text)
        # print("搜索引擎模式:", " ".join(seg_list))

