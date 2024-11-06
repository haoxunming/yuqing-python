import scrapy
import json
import jieba
from datetime import datetime
import pyplutchik
import sys
import re
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import numpy as np
from selenium.webdriver.chrome.service import Service

# sys.path += ['./', '../']  # allow 'shared' to be imported below
# import shared.common as c
# import shared.config as config
# from shared.mysql_helper import use_mysql
import mysql.connector
from mysql.connector import Error
from urllib.parse import urlparse, parse_qs

from transformers import BertTokenizer, BertForSequenceClassification
import torch
import os

class XinlangSpider(scrapy.Spider):
    name = "xinlang"
    allowed_domains = ["sina.com.cn"]
    # start_urls = ["https://news.sina.com.cn"]
    # 实例化一个浏览器对象
    # def __init__(self, *args, **kwargs):
    #     super(XinlangSpider, self).__init__(*args, **kwargs)
    #
    #     chrome_options = Options()
    #     chrome_options.add_argument('--headless')
    #     # 使用无头模式，无 GUI的Linux服务器必须添加
    #     chrome_options.add_argument('--disable-gpu')
    #     # 不使用GPU，有的机器不支持GPU
    #     chrome_options.add_argument('--no-sandbox')
    #     # 运行 Chrome 的必需参数
    #     chrome_options.add_argument('--disable-dev-shm-usage')
    #     chrome_options.add_argument("--remote-debugging-port=9222")
    #     # 以上两个参数具体作用不明，但笔者机器需要这两个参数才能运行
    #     # chrome_options.add_argument("user-agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'")
    #     # 该参数用于避免被认出，非必需参数
    #     # 设置 ChromeDriver 的路径
    #     # chrome_driver_path = '/opt/software/anaconda3/envs/collection_project/bin/chromedriver'
    #
    #     # 初始化 WebDriver
    #     # service = Service(chrome_driver_path)
    #     self.driver = webdriver.Chrome(options=chrome_options)
    #     # 初始化 WebDriver
    #     # dirver = webdriver.Chrome()
    #     # self.bro = webdriver.Chrome(executable_path='驱动路径')

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
                # 获取关键词
                cursor.execute("select id,programme_name,key_words from t_programme")
                records = cursor.fetchall()
                print("Number of rows in table: ", cursor.rowcount)

                for row in records:
                    if row['key_words']:
                        keywords = row['key_words'].split('、')
                        for keyword in keywords:
                            if keyword and keyword.strip() not in keyword_list:
                                keyword_list.append(keyword.strip())

                # 获取爬虫类型
                cursor.execute("select id,label,value from t_dict_data where dict_type = 'crawler_platform'")
                records = cursor.fetchall()
                for row in records:
                    if row['label'] not in data_type:
                        data_type[row['label']] = row['value']
                if data_type:
                    self.data_type = data_type

                # 获取情感类型
                cursor.execute("select id,label,value from t_dict_data where dict_type = 'emotional_attribute'")
                records = cursor.fetchall()
                for row in records:
                    if row['label'] not in emotional_data_type:
                        emotional_data_type[row['label']] = row['value']

                if emotional_data_type:
                    self.emotional_data_type = emotional_data_type

                # 获取情感类型
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
        self.exit_link_list = {}
        self.models_index_urls = []
        self.models_detail_urls = []
        for keyword in keyword_list:
            url = 'https://search.sina.com.cn/?c=news&q={}'.format(keyword)
            self.models_index_urls.append(url)
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        print(f'######################################{response.url}########################################')
        # 获取所有具有mid属性的div.card-wrap元素
        card_wraps = response.css('div.result div.box-result h2 a::attr(href)').getall()
        for detail_lin in card_wraps:
            if 'video.sina.com.cn' in detail_lin:
                continue
                yield scrapy.Request(url=response.urljoin(detail_lin), callback=self.parse_world_video)
            else:
                # 获取详情页链接（用于selenium伪浏览器爬取）
                self.models_detail_urls.append(detail_lin)
                yield scrapy.Request(url=response.urljoin(detail_lin), callback=self.parse_world)

        # last_li = response.css('div.m-page div span.list ul li:last-child')
        # last_page = response.css('div.result table div.pagebox a:last-child::text').get()

        # 自定义获取页数
        # 解析URL
        parsed_url = urlparse(response.url)
        # 获取查询参数
        query_params = parse_qs(parsed_url.query)
        # 获取参数 q 的值
        q_value = query_params.get('q', [''])[0]
        if q_value:
            self.exit_link_list[q_value] = 0


        if q_value:
            page_len = 30 if self.exit_link_list[q_value] > 30 else self.exit_link_list[q_value]
            last_list = response.css('div.result table div.pagebox a')
            if last_list and self.exit_link_list[q_value] < page_len:
                last_page = last_list[len(last_list)-1].css('::text').get()
                if last_page == '下一页':
                    info_url = last_list[len(last_list)-1].css('::attr(href)').get()
                    print("info_url:", info_url)
                    # 使用正则表达式匹配整个参数字符串（包括单引号）
                    # match = re.search(r"'\?[^']*'", info_url)
                    match = re.search(r"linkPostPage\('([^']*)','([^']*)'\)", info_url)
                    if match:
                        # 提取'/news'
                        news_path = match.group(1)
                        # 提取查询字符串
                        query_string = match.group(2)
                        # 去除匹配结果中的单引号，得到纯查询字符串
                        # query_string = match.group(0)[1:-1]
                        # print(query_string)
                        url = 'https://search.sina.com.cn{}{}'.format(news_path, query_string)

                        # 自定义 页数
                        self.exit_link_list[q_value] = self.exit_link_list[q_value] + 1

                        yield scrapy.Request(url, callback=self.parse)
                    else:
                        print("未找到匹配的查询字符串")


    # def parse(self, response):
    #     for href in response.css('#blk_cNav2_01 a::attr(href)').getall():
    #         yield scrapy.Request(url=response.urljoin(href), callback=self.parse_news)

    def parse_news(self, response):
        # 解析新闻详情页，提取所需数据
        print(f'==============={response.url}===================')
        # 处理类型滚动新闻
        # if response.url.startswith('https://news.sina.com.cn/roll'):
        #     for href in response.css('#blk_cNav2_01 a::attr(href)').getall():
        #         yield scrapy.Request(url=response.urljoin(href), callback=self.parse_world)

        # 处理类型排行新闻
        # if response.url.startswith('https://news.sina.com.cn/hotnews'):
        #     for href in response.css('#blk_cNav2_01 a::attr(href)').getall():
        #         yield scrapy.Request(url=response.urljoin(href), callback=self.parse_world)

        # 处理类型政务新闻
        # if response.url.startswith('http://gov.sina.com.cn'):
        #     for href in response.css('#blk_cNav2_01 a::attr(href)').getall():
        #         yield scrapy.Request(url=response.urljoin(href), callback=self.parse_world)

        # 处理类型国内新闻
        # if response.url.startswith('https://news.sina.com.cn/china'):
        #     type_str = '国内'
        #     info_url = 'https://feed.sina.com.cn/api/roll/get?pageid=121&lid=1356&num=20&versionNumber=1.2.4&page=1'
        #     yield scrapy.Request(url=info_url, callback=self.parse_china, meta={'type_str': type_str, 'page_num': 1})

        # 处理类型国际新闻
        if response.url.startswith('https://news.sina.com.cn/world'):
            type_str = '国际'
            for href in response.css('#subShowContent1_static h2 a::attr(href)').getall():
                yield scrapy.Request(url=response.urljoin(href), callback=self.parse_world, meta={'type_str': type_str})

        # 处理类型军事新闻
        # if response.url.startswith('https://mil.news.sina.com.cn'):
        #     for href in response.css('#blk_cNav2_01 a::attr(href)').getall():
        #         yield scrapy.Request(url=response.urljoin(href), callback=self.parse_world)

        # 处理类型军事新闻
        # if response.url.startswith('https://mil.news.sina.com.cn'):
        #     for href in response.css('#blk_cNav2_01 a::attr(href)').getall():
        #         yield scrapy.Request(url=response.urljoin(href), callback=self.parse_world)

    # 使用 NLTK 库中的 VADER（Valence Aware Dictionary and sEntiment Reasoner）工具。VADER 是一种基于词典和启发式的情感分析工具，特别适合社交媒体文本的情感分析
    # 步骤
    # 安装 NLTK 和 VADER
    # 首先确保安装了 NLTK 库（pip install nltk），并下载了 VADER 词典。
    # 注意事项
    # 确保已经下载了 vader_lexicon。
    # 如果你的文本是中文，VADER 默认不支持中文。你可能需要寻找其他的中文情感分析库，例如 SnowNLP 或者使用预训练的模型进行中文情感分析。
    # def get_text_Analyzer(text):
    #     import nltk
    #     from nltk.sentiment import SentimentIntensityAnalyzer
    #     # 下载 VADER 词典
    #     nltk.download('vader_lexicon')
    #     # 初始化情感分析器
    #     sia = SentimentIntensityAnalyzer()
    #
    #     # text=待分析的文本
    #     # text = "I love using Python for natural language processing tasks!"
    #
    #     # 进行情感分析
    #     scores = sia.polarity_scores(text)
    #
    #     # 输出情感分析结果
    #     print("情感分析结果：", scores)
    #
    #     scores_result = None
    #
    #     # 判断情感极性
    #     if scores['compound'] >= 0.05:
    #         scores_result = '正面'
    #     elif scores['compound'] <= -0.05:
    #         scores_result = '负面'
    #     else:
    #         scores_result = '中性'
    #     return scores_result

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
        keywords = ['愤怒', '生气', '恼火', '气愤', '霸凌', '欺凌', '糟糕', '失败', '差劲', '痛苦', '悲伤', '失望', '不幸', '糟糕透顶',
        '困难', '艰难', '困惑', '沮丧', '绝望', '糟糕的', '失败的', '不好的',
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

    # 使用BERT进行中文情感分析
    def get_text_Bert(self, text):
        import torch
        from transformers import BertTokenizer, BertForSequenceClassification
        model_dir = 'D:\\myTool\\bert-base-chinese'
        # 加载预训练的 BERT 模型和分词器
        # tokenizer = BertTokenizer.from_pretrained("bert-base-chinese")
        tokenizer = BertTokenizer.from_pretrained(model_dir)
        # model = BertForSequenceClassification.from_pretrained("bert-base-chinese")
        # model = BertForSequenceClassification.from_pretrained(model_dir)

        # 示例文本
        # text = "这家餐厅的服务很好，食物也很美味。"

        # 对文本进行编码
        inputs = tokenizer(text, return_tensors="pt")

        print(inputs)

        # 获取模型输出
        # with torch.no_grad():
        #     outputs = model(**inputs)

        # 获取预测概率
        # probabilities = torch.softmax(outputs.logits, dim=1).numpy()[0]

        # 输出结果
        # positive_prob = probabilities[1]  # 假设标签 1 表示正面情感
        # negative_prob = probabilities[0]  # 假设标签 0 表示负面情感

        # print("正面概率:", positive_prob)
        # print("负面概率:", negative_prob)

        # 判断情感倾向
        # if positive_prob > negative_prob:
        #     print("正面评价")
        # else:
        #     print("负面评价")
    # 滚动新闻详情页
    def parse_roll(self, response):
        pass

    # 排行新闻详情页
    def parse_hotnews(self, response):
        pass

    # 政务新闻详情页
    def parse_gov(self, response):
        pass

    # 国内新闻详情页
    def parse_china(self, response):
        type_str = response.meta.get('type_str')
        page_num = response.meta.get('page_num')
        json_str = response.text
        try:
            if json_str:
                # 将JSON字符串转换为Python字典
                json_data = json.loads(json_str)

                if 'result' in json_data and json_data['result']:
                    self.current_page_items_count = len(json_data['result']['data'])

                if json_data['result']['data'] and len(json_data['result']['data']) > 0:
                    for item in json_data['result']['data']:
                        # 在这里处理每个数据项
                        yield scrapy.Request(url=response.urljoin(item['url']), callback=self.parse_china_detail,
                                             meta={'type_str': type_str})

                if hasattr(self, 'current_page_items_count'):
                    if not self.current_page_items_count or self.current_page_items_count == 0:
                        return
                info_url = 'https://feed.sina.com.cn/api/roll/get?pageid=121&lid=1356&num=20&versionNumber=1.2.4&page={}'
                urls = info_url.format(page_num + 1)
                yield scrapy.Request(url=urls, callback=self.parse_china, meta={'type_str': type_str, 'page_num': page_num + 1})
            # 现在你可以像处理普通Python字典一样处理json_data了
            # 例如，打印某个键的值
            # print(json_data['title'])

            # 你可以在这里进一步处理数据，比如生成Item对象
            # ...

        except json.JSONDecodeError:
            # 处理解析JSON时可能出现的错误
            self.logger.error('解析JSON时出错: {}'.format(response.url))

    def parse_china_detail(self, response):
        # 采集网站名称
        type_str = response.meta.get('type_str')
        # 标题
        title = response.css('.main-title::text').get()
        # 作者
        author = response.css('.show_author::text').get()
        # 注意：strip=True用于去除文本前后的空白符
        # date = response.css('.date-source .date::text').get(strip=True)
        # 发布日期
        # date = response.css('.date-source .date::text').get()
        date_format = "%Y年%m月%d日 %H:%M"
        date_string = response.css('.date-source .date::text').get()
        dt = datetime.strptime(date_string, date_format)
        date = dt.timestamp() * 1000
        # content = response.css('#article::text').get()
        # 内容
        content = '\n'.join(response.css('div.article p::text').extract())
        # 情感分析
        snowNLP_anay = self.get_text_SnowNLP(content) if content else None
        # 情感分析
        snowNLP_anay = self.emotional_data_type[snowNLP_anay] if snowNLP_anay else self.emotional_data_type['中性']
        # 关键词
        keywords = ';'.join(response.css('div.article-bottom div.keywords a::text').getall())
        if not keywords:
            keywords = self.cut_word(title)
        # 发布来源
        source = response.css('.date-source .source::text').get()
        # 评论数
        comments_num = response.css('.sina-comment-top .clearfix span em a::text').get()
        # 原文链接
        qriginal_link = response.url

        yield {
            'type_str': type_str,
            'title': title,
            'snowNLP_anay': snowNLP_anay,
            'author': author,
            'date': date,
            'date_str': str(date),
            'content': content,
            'comments_count': int(comments_num) if comments_num else 0,
            'keywords': keywords,
            'qriginal_link': qriginal_link,
            'source': source,
            'source_platform': 1
        }

    # 国际新闻详情页
    def parse_world(self, response):
        # 采集网站名称
        # type_str = response.meta.get('type_str')
        source_platform = self.data_type['新浪']
        snowNLP_anay = None
        snowNLP_anay_score = None
        # 标题
        title = response.css('.main-title::text').get()
        if not title:
            title = response.css('div.F_con div.Vd_titBox h2::text').get()
        # 作者
        author = response.css('.show_author::text').get()
        if not author:
            author = response.css('.date-source span.author a::text').get()
        # 注意：strip=True用于去除文本前后的空白符
        # date = response.css('.date-source .date::text').get(strip=True)
        # 发布日期
        # date = response.css('.date-source .date::text').get()
        date_string = response.css('.date-source .date::text').get()
        if not date_string:
            date_string = response.css('div.article-box div.article-header p.source-time span:first-of-type::text').get()
            if not date_string:
                date_string = response.css('div.vd_vedioinfo div.vedioinfo_inner p.from span:first-of-type em::text').get()

        # dt = datetime.strptime(date_string, date_format) if date_string else None
        # 定义两种日期格式
        date_formats = ['%Y年%m月%d日 %H:%M', '%Y年%m月%d日 %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S']

        # 尝试解析日期字符串
        dt = None
        if date_string:
            for fmt in date_formats:
                try:
                    dt = datetime.strptime(date_string, fmt)
                    break
                except ValueError:
                    continue

        date = dt.timestamp() * 1000 if dt else None
        # content = response.css('#article::text').get()
        # 内容
        content_list = response.css('div.article p::text').extract()
        content = '\n'.join(response.css('div.article p::text').extract()) if content_list else None
        if not content:
            content_list_two = response.css('div.article::text').extract()
            content = '\n'.join(response.css('div.article::text').extract()) if content_list_two else None
            if content:
                conten_list_three = response.css('div.article div.Video_Cont div#myMovie video::attr(src)').get()
                if conten_list_three:
                    content += '\n' + response.css('div.article div.Video_Cont div#myMovie video::attr(src)').get()
            else:
                content = response.css('div.article div.Video_Cont div#myMovie video::attr(src)').get()
        # snowNLP_anay = self.get_text_SnowNLP(content)

        # 情感分析
        if content:
            snowNLP_anay, snowNLP_anay_score = self.get_text_SnowNLP(content)
        # 情感分析
        snowNLP_anay = self.emotional_data_type[snowNLP_anay] if snowNLP_anay else self.emotional_data_type['中性']
        # 情绪类型
        emotion_type = self.emotional_type[snowNLP_anay_score] if snowNLP_anay_score else self.emotional_type['喜悦']

        # 关键词
        keywords = ';'.join(response.css('div.article-bottom div.keywords a::text').getall())
        if not keywords and title:
            keywords = self.cut_word(title)
        # 发布来源
        source = response.css('.date-source .source::text').get()
        if not source:
            source = response.css('div.vd_vedioinfo div.vedioinfo_inner p.from span:last-of-type a::text').get()
        # 评论数
        comments_num = response.css('.sina-comment-top .clearfix span em a::text').get()
        # 原文链接
        qriginal_link = response.url
        yield {
            'type_str': '新浪',
            'title': title,
            'author': author,
            'keywords': keywords,
            'pulish_region': '暂无',  # 发布区域(默认值)
            'date': date,
            'date_str': str(date) if date else None,
            'content': content,
            'source': source,
            'reposts_count': 0,  # 转发数
            'comments_count': int(comments_num) if comments_num else 0,
            'attitudes_count': 0,  # 点赞数
            'collects_count': 0,  # 收藏数
            'source_platform': source_platform,
            'qriginal_link': qriginal_link,
            'snowNLP_anay': snowNLP_anay,
            'emotion_type': emotion_type
        }

    def parse_world_video(self, response):
        # 采集网站名称
        type_str = response.meta.get('type_str')
        # 标题
        title = response.css('.main-title::text').get()
        if not title:
            title = response.css('div.F_con div.Vd_titBox h2::text').get()
        # 作者
        author = response.css('.show_author::text').get()
        if not author:
            author = response.css('.date-source span.author a::text').get()
        # 注意：strip=True用于去除文本前后的空白符
        # date = response.css('.date-source .date::text').get(strip=True)
        # 发布日期
        # date = response.css('.date-source .date::text').get()
        date_format = "%Y年%m月%d日 %H:%M"
        date_format_1 = "%Y-%m-%d %H:%M"
        date_format_2 = "%Y-%m-%d %H:%M:%S"
        date_string = response.css('.date-source .date::text').get()
        if not date_string:
            date_string = response.css('div.article-box div.article-header p.source-time span:first-of-type::text').get()
            if date_string:
                date_format = date_format_1
            else:
                date_string = response.css('div.vd_vedioinfo div.vedioinfo_inner p.from span:first-of-type em::text').get()
                if date_string:
                    date_format = date_format_2
            print('date_string is None')
        dt = datetime.strptime(date_string, date_format)
        date = dt.timestamp() * 1000
        # content = response.css('#article::text').get()
        # 内容
        content_list = response.css('div.article p::text').extract()
        content = '\n'.join(response.css('div.article p::text').extract()) if content_list else None
        if not content:
            content_list_two = response.css('div.article::text').extract()
            content = '\n'.join(response.css('div.article::text').extract()) if content_list_two else None
            if content:
                conten_list_three = response.css('div.article div.Video_Cont div#myMovie video::attr(src)').get()
                if conten_list_three:
                    content += '\n' + response.css('div.article div.Video_Cont div#myMovie video::attr(src)').get()
            else:
                content = response.css('div.article div.Video_Cont div#myMovie video::attr(src)').get()
        # snowNLP_anay = self.get_text_SnowNLP(content)
        # 情感分析
        snowNLP_anay = self.get_text_SnowNLP(content) if content else None
        # 情感分析
        snowNLP_anay = self.emotional_data_type[snowNLP_anay] if snowNLP_anay else self.emotional_data_type['中性']

        # 关键词
        keywords = ';'.join(response.css('div.article-bottom div.keywords a::text').getall())
        if not keywords and title:
            keywords = self.cut_word(title)
        # 发布来源
        source = response.css('.date-source .source::text').get()
        if not source:
            source = response.css('div.vd_vedioinfo div.vedioinfo_inner p.from span:last-of-type a::text').get()
        # 评论数
        comments_num = response.css('.sina-comment-top .clearfix span em a::text').get()
        # 原文链接
        qriginal_link = response.url
        yield {
            'type_str': type_str,
            'title': title,
            'snowNLP_anay': snowNLP_anay,
            'author': author,
            'date': date,
            'date_str': str(date),
            'content': content,
            'comments_num': int(comments_num) if comments_num else 0,
            'qriginal_link': qriginal_link,
            'keywords': keywords,
            'source': source,
            'source_platform': 1
        }

    # 军事新闻详情页
    def parse_mil(self, response):
        pass

    # 你需要实现这个函数来计数页面上的数据项
    def count_items_on_page(self, response):
        # 这里应该根据你的页面结构来编写计数逻辑
        # 例如，可以计算某个特定class的元素数量
        return len(response.css('some-selector'))

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

    # def get_cement(self, text):
    #     from cement import Cement
    #
    #     # 示例文本
    #     text = "这家餐厅的服务很好，食物也很美味。"
    #
    #     # 初始化情绪分析器
    #     em = Cement()
    #
    #     # 分析文本
    #     result = em.analyze(text)

    def get_pyplutchik(self, text):
        # from pyplutchik import Plutchik

        # 创建Plutchik对象
        plutchik = pyplutchik.Plutchik()

        # 待分析的文本
        text = "这是一段很好的文本，我们将使用Pyplutchik来分析它的情感和关键词。"

        # 进行情感分析
        sentiment_analysis = plutchik.get_sentiment(text)
        print("情感分析:", sentiment_analysis)

    # 关闭浏览器
    # def closed(self, spider):
    #     self.driver.quit()


if __name__ == '__main__':
    text = '你听过希伯来语的那首“明年我们将杀死所有人”的儿童歌曲吗'
    # sdf = XinlangSpider().get_text_Bert(text)
    sdf = XinlangSpider().get_pyplutchik(text)
    print(sdf)
