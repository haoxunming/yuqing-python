import scrapy
import math
import mysql.connector
from DrissionPage._configs.chromium_options import ChromiumOptions
from mysql.connector import Error
import jieba
from urllib.parse import urljoin
from tqdm import tqdm
import time
from datetime import datetime, timedelta
import random
import spacy
from snownlp import SnowNLP
import numpy as np
from DrissionPage import ChromiumPage
# from DrissionPage import FirefoxPage
from urllib.parse import quote

from transformers import BertTokenizer, BertForSequenceClassification
import torch
import os

class XiaohongshuSpider(scrapy.Spider):
    name = "xiaohongshu"
    allowed_domains = ["xiaohongshu.com"]
    # start_urls = ["https://xiaohongshu.com"]
    def __init__(self, *args, **kwargs):
        super(XiaohongshuSpider, self).__init__(*args, **kwargs)
        co = ChromiumOptions()
        # co.incognito(True)
        # 使用无头模式，无 GUI的Linux服务器必须添加
        # co.headless(True)
        # co.set_local_port(7890)
        # co.set_user_agent('')
        # 1、设置无头模式：co.headless(True)
        # 2、设置无痕模式：co.incognito(True)
        # 3、设置访客模式：co.set_argument('--guest')
        # 4、设置请求头user-agent：
        co.set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36')
        # 5、设置指定端口号：co.set_local_port(7890)
        # 6、设置代理：co.set_proxy('http://localhost:2222')


        self.page = ChromiumPage(co)

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
        # 1、第1次运行需要登录，需要执行sign_in()步骤。第2次之后不用登录，可以注释掉sign_in()步骤。
        self.sign_in()
        # self.default_headers = self.settings.get('DEFAULT_REQUEST_HEADERS')
        keyword_list = self.get_mysql_data()
        if not keyword_list:
            return None
        for keyword in keyword_list:
            author_url = "https://www.xiaohongshu.com/search_result?keyword={}&source=web_user_page".format(keyword)
            yield scrapy.Request(author_url, callback=self.parse)

    def parse(self, response):
        self.list_data = []

        # 2、设置主页地址url
        author_url = response.url

        # 3、设置向下翻页爬取次数
        # 根据小红书作者主页“当前发布笔记数”计算浏览器下滑次数。
        # “当前发布笔记数” 获取方法参考https://www.sohu.com/a/473958839_99956253
        # note_num是笔记数量
        note_num = 10
        # times是计算得到的翻页次数，笔记数量除以20，调整系数，再向上取整
        times = math.ceil(note_num / 20 * 1.1)
        print(f"需要执行翻页次数为：{times}")

        # 下面不用改，程序自动执行
        # 打开主页
        self.open_url_dp(author_url)

        # 根据设置的次数，开始爬取数据
        self.my_xhs_crawler(times)

        if self.list_data:
            data_dict_list = self.my_crawler_detail_data()
            for data_dict in data_dict_list:
                yield data_dict

    def countdown(self, n):
        for i in range(n, 0, -1):
            print(f'\r倒计时{i}秒', end='')  # \r让光标回到行首 ，end=''--结束符为空，即不换行
            time.sleep(1)  # 让程序等待1秒
        else:
            print('\r倒计时结束')

    def sign_in(self):
        # sign_in_page = ChromiumPage()
        self.page.get('https://www.xiaohongshu.com')
        # 第一次运行需要扫码登录
        print("请扫码登录")
        # 倒计时30s
        self.countdown(30)


    def open_url_dp(self, url):
        # self.page = ChromiumPage()
        # self.page.set.header(name='key', value='val')
        self.page.get(f'{url}')
        # self.page.set.cookies({
        #     'xsecappid': 'xhs-pc-web',
        #     'gid': 'yY0J8J2fW8TqyY0J8J2Sfk7fdi4vVEDVI9q794v2jf2Ui428S2MFu9888KW4j4K8JYDdi0j4',
        #     'abRequestId': 'da6998a2-bd3f-50f4-bad9-fa23bd00f60f',
        #     'webBuild': '4.31.6',
        #     'a1': '19192184045qwwdb1ow6zfu7lfq1lmngspdzlq1ls50000283282',
        #     'webId': '9a610c2ac017f01446ebcaf77c0cec57',
        #     'unread': '{"ub":"66c2ba55000000001e01bef8","ue":"66b56aa60000000025031cf4","uc":12}',
        #     'acw_tc': '1d9843e472e6c3f275cdfa75025d5d976c167fca272a6300116f70056d028f68',
        #     'websectiga': '10f9a40ba454a07755a08f27ef8194c53637eba4551cf9751c009d9afb564467',
        #     'sec_poison_id': 'a06f5c2c-3718-4de0-9bd5-d8361ce4edc3',
        #     'web_session': '040069b39b27722e14faa297fb344bb1a299f3'})



        # 页面最大化
        self.page.set.window.max()

        # 定位作者信息
        # user = page.ele('.info')
        # 作者名字
        # author = user.ele('.user-name', timeout=0).text

    def get_info(self):
        # notes列表存放当前页面的笔记
        notes = []
        base_url = "https://www.xiaohongshu.com"
        # 定位包含笔记信息的sections
        container = self.page.ele('.feeds-container')
        sections = container.eles('.note-item')

        for section in sections:
            # 笔记类型
            if section.ele('.play-icon', timeout=0):
                note_type = "视频"
            else:
                note_type = "图文"
            # 文章链接
            if section.ele('tag:a'):
                note_link = section.ele('tag:a', timeout=0).link
                # 构建完整的链接
                complete_note_link = urljoin(base_url, note_link)
            else:
                continue
            # 标题
            footer = section.ele(".footer")
            if not footer:
                continue

            if footer.ele('.title'):
                title = footer.ele('.title', timeout=0).text
            else:
                title = None

            print(f"第{self.i}条笔记：{note_type}，{title}")
            # 作者
            author_wrapper = footer.ele('.author-wrapper')

            # 作者
            author = author_wrapper.ele('.name', timeout=0).text

            self.list_data.append([note_type, title, author, complete_note_link])

        # 写入数据，r为全局变量
        # r.add_data(notes)

    def parse_time(self, time_str):
        # 解析字符串
        if '今天' in time_str:
            date_part = datetime.now().date()
            time_part = time_str.split(' ')[1]
        elif '昨天' in time_str:
            date_part = datetime.now().date() - timedelta(days=1)
            time_part = time_str.split(' ')[1]
        elif '前天' in time_str:
            date_part = datetime.now().date() - timedelta(days=2)
            time_part = time_str.split(' ')[1]
        elif '天前' in time_str:
            time_ary = time_str.split(' ')
            date_part = datetime.now().date() - timedelta(days=int(time_ary[0]))
            time_part = '00:00'
        elif '编辑于' in time_str:
            # 编辑于
            time_ary = time_str.split(' ')
            time_ary_two = time_ary[1].split('-')
            year = datetime.now().date().year
            if len(time_ary_two) == 3:
                date_part = datetime(int(time_ary_two[0]), int(time_ary_two[1]), int(time_ary_two[2]))
            if len(time_ary_two) == 2:
                date_part = datetime(year, int(time_ary_two[0]), int(time_ary_two[1]))
            time_part = '00:00'
        elif '-' in time_str and ':' not in time_str:
            # 仅日期，没有时间
            parts = time_str.split('-')
            if len(parts) == 3:
                year, month, day = map(int, parts)
                date_part = datetime(year, month, day)
            else:
                # 假设当前年份
                year = datetime.now().year
                month, day = map(int, parts)
                date_part = datetime(year, month, day)
            time_part = '00:00'
        elif '-' in time_str and ':' in time_str:
            # 包含日期和时间
            parts = time_str.split(' ')
            date_part = datetime.strptime(parts[0], '%Y-%m-%d')
            time_part = parts[1]
        else:
            raise ValueError('Unsupported format')

        # 解析时间
        if ':' in time_part and len(time_part.split(':')) == 3:
            hour, minute, second = map(int, time_part.split(':'))

        if ':' in time_part and len(time_part.split(':')) == 2:
            hour, minute = map(int, time_part.split(':'))
            second = 0  # 默认秒为0

        # 创建 datetime 对象
        dt = datetime(date_part.year, date_part.month, date_part.day, hour, minute, second)

        return dt

    def page_scroll_down(self):
        print(f"********下滑页面********")
        self.page.scroll.to_bottom()
        # 生成一个1-2秒随机时间
        random_time = random.uniform(1, 2)
        # 暂停
        time.sleep(random_time)

    def my_crawler_detail_data(self):
        source_platform = self.data_type['小红书']
        data_dict_list = []
        for data in self.list_data:
            title = data[1]

            self.page.get(data[3])
            note_container = self.page.ele('.note-container')

            publish_time = None
            publish_city = None
            contet_desc = None
            like_count, collect_count, chat_count = None, None, None

            if note_container:
                # 获取笔记内容
                content = note_container.ele('.interaction-container')
                if content:
                    contet_desc = content.ele('.note-scroller').ele('.note-content').ele('.desc').text
                    bottom_content = content.ele('.note-scroller').ele('.note-content').ele('.bottom-container').ele('.date').text
                    if bottom_content:
                        cottom_content_array = bottom_content.split(' ')
                        if len(cottom_content_array) == 4:
                            publish_time = cottom_content_array[1] + " " + cottom_content_array[2]
                            publish_city = cottom_content_array[3]

                        if len(cottom_content_array) == 3:
                            publish_time = cottom_content_array[0] + " " + cottom_content_array[1]
                            publish_city = cottom_content_array[2]

                        if len(cottom_content_array) == 2:
                            if cottom_content_array[0] in ['今天', '昨天', '前天', '编辑于']:
                                publish_time = cottom_content_array[0] + " " + cottom_content_array[1]
                                publish_city = '暂无'
                            else:
                                # 发布时间
                                publish_time = cottom_content_array[0]
                                # 发布地
                                publish_city = cottom_content_array[1]
                        if len(cottom_content_array) == 1:
                            # 发布时间
                            publish_time = cottom_content_array[0]
                            # 发布地
                            publish_city = '暂无'

                    count_contair = content.ele('.input-box').ele('.left')
                    if count_contair:
                        # 点赞数
                        like_count = self.convert_likes(count_contair.ele('.like-wrapper like-active').ele('.count').text)
                        # 收藏数
                        collect_count = self.convert_likes(count_contair.ele('.collect-wrapper').ele('.count').text)
                        # 评论数
                        chat_count = self.convert_likes(count_contair.ele('.chat-wrapper').ele('.count').text)

            snowNLP_anay, snowNLP_anay_score = '中性', '喜悦'

            if contet_desc and not title:
                title = self.get_first_sentence(contet_desc)

            snowNLP_anay, snowNLP_anay_score = self.get_text_SnowNLP(contet_desc)
            # 情感分析
            snowNLP_anay = self.emotional_data_type[snowNLP_anay] if snowNLP_anay else self.emotional_data_type['中性']
            # 情绪类型
            emotion_type = self.emotional_type[snowNLP_anay_score] if snowNLP_anay_score else self.emotional_type['喜悦']

            keywords = None
            if title:
                keywords = self.cut_word(title)

            if publish_time:
                dt = self.parse_time(publish_time)
                publish_time = dt.timestamp() * 1000
            else:
                print(f'时间异常============================{data[3]}')



            data_dict = {
                'type_str': '小红书',
                'title': title,
                'author': data[2],
                'keywords': keywords,
                'pulish_region': publish_city,  # 发布区域(默认值)
                'date': publish_time,
                'date_str': str(publish_time) if publish_time else None,
                'content': contet_desc,
                'source': '小红书',
                'reposts_count': 0,  # 转发数
                'comments_count': chat_count,
                'attitudes_count': like_count,  # 点赞数
                'collects_count': collect_count,  # 收藏数
                'source_platform': source_platform,
                'qriginal_link': data[3],
                'snowNLP_anay': snowNLP_anay,
                'emotion_type': emotion_type
            }

            data_dict_list.append(data_dict)
        return data_dict_list

    def my_xhs_crawler(self, times):
        for i in tqdm(range(1, times + 1)):
            self.i = i
            self.get_info()
            self.page_scroll_down()

    # 定义转换点赞数的函数
    def convert_likes(self, likes):
        # 确保likes是字符串类型
        if isinstance(likes, int):
            likes = str(likes)
        # 移除'+'字符
        likes = likes.replace('+', '')
        # 检查是否包含'万'或'千'单位，并进行相应的转换
        if '万' in likes:
            # return int(likes.replace('万', '')) * 10000
            # 移除“万”并转换为浮点数，再乘以10000
            return float(likes.replace('万', '')) * 10000
        elif '千' in likes:
            # return int(likes.replace('千', '')) * 1000
            # 移除“千”并转换为浮点数，再乘以1000
            return float(likes.replace('千', '')) * 1000
        elif '赞' in likes or '评' in likes or '藏' in likes:
            return 0
        else:
            return int(likes)

    def get_first_sentence(self, text):
        # 加载 spaCy 模型
        nlp = spacy.load('zh_core_web_sm')
        # 使用 spaCy 分割句子
        doc = nlp(text)
        if doc.sents:
            return next(doc.sents).text.strip()
        else:
            return ""

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

    def cut_word(self, text):
        # 精确模式
        seg_list = jieba.cut(text, cut_all=False)
        seg_list_word = []
        for item in seg_list:
            if len(item) > 1:
                seg_list_word.append(item)

        return ";".join(seg_list_word)

    def closed(self, spider):
        self.page.quit()

