# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from selenium import webdriver
# 导入动作链
from selenium.webdriver import ActionChains
import time
from scrapy.http import HtmlResponse
from scrapy import signals
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class SeleniumMiddleware(object):
    def process_request(self, request, spider):
        url = request.url
        dirver = spider.driver  # 获取在爬虫类中定义的浏览器对象

        if url in spider.models_detail_urls:
            dirver.get(url)  #对详情页发起请求
            time.sleep(3)  # 睡眠3秒
            data = dirver.page_source  # 获取网页源码（包含了动态加载的数据）

            # 响应获取到的网页源码（包含了动态加载的数据）
            res = HtmlResponse(url=url, body=data, encoding='utf-8', request=request)

            return res

        # if url in spider.models_index_urls:
        #     dirver.get(url)  # 对详情页发起请求
        #     time.sleep(3)  # 睡眠3秒
        #     data = dirver.page_source  # 获取网页源码（包含了动态加载的数据）
        #     # 响应获取到的网页源码（包含了动态加载的数据）
        #     res = HtmlResponse(url=url, body=data, encoding='utf-8', request=request)
        #
        #     div_with_class = res.css('div.sina-verification')
        #     # 如果存在滑块验证
        #     if div_with_class:
        #         print(f'=====================开始滑块验证====================================')
        #         # 定位滑块元素
        #         slide = dirver.find_element_by_css_selector(".sina-verification-bar")
        #         action = ActionChains(dirver)  # 创建动作链对象
        #         # click_and_hold:点击并按住, perform()执行
        #         action.click_and_hold(slide).perform()
        #         action.move_by_offset(85, 0)
        #         action.move_by_offset(85, 0)
        #         action.move_by_offset(85, 0)
        #         action.move_by_offset(85, 0)
        #
        #         # 释放
        #         action.release().perform()
        #
        #     return res
    # def process_request(self, request, spider):
    #     url = request.url
    #     if '/w' in url or '/o' in url or '/c' in url or 'finance.sina.com.cn' in url or 'k.sina.com.cn' in url:
    #         chrome_options = Options()
    #         chrome_options.add_argument('--headless')
    #         # 使用无头模式，无 GUI的Linux服务器必须添加
    #         chrome_options.add_argument('--disable-gpu')
    #         # 不使用GPU，有的机器不支持GPU
    #         chrome_options.add_argument('--no-sandbox')
    #         # 运行 Chrome 的必需参数
    #         chrome_options.add_argument('--disable-dev-shm-usage')
    #         chrome_options.add_argument("--remote-debugging-port=9222")
    #         # 以上两个参数具体作用不明，但笔者机器需要这两个参数才能运行
    #         # chrome_options.add_argument("user-agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'")
    #         # 该参数用于避免被认出，非必需参数
    #         # 设置 ChromeDriver 的路径
    #         # chrome_driver_path = '/opt/software/anaconda3/envs/collection_project/bin/chromedriver'
    #
    #         # 初始化 WebDriver
    #         # service = Service(chrome_driver_path)
    #         dirver = webdriver.Chrome(options=chrome_options)
    #         # 初始化 WebDriver
    #         # dirver = webdriver.Chrome()
    #         dirver.get(url)
    #         time.sleep(3)
    #         data = dirver.page_source
    #         dirver.close()
    #         res = HtmlResponse(url=url, body=data, encoding='utf-8', request=request)
    #
    #         return res



class WebsiteXinlangSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class WebsiteXinlangDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
