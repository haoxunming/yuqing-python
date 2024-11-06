# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import pymysql
from scrapy import signals
from random import choice
from scrapy.exceptions import NotConfigured

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class WebsiteWeiboSpiderMiddleware:
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


class WebsiteWeiboDownloaderMiddleware:
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

class ProxyMiddleware(object):
    # ============================从数据库获取动态ip=================================
    # def __init__(self):
    #     self.conn = pymysql.connect(
    #         host='127.0.0.1',
    #         user='username',
    #         passwd='userpassword',
    #         db='proxy_ip',
    #         charset='utf8'
    #     )
    #     self.cursor = self.conn.cursor()
    #
    # def get_random_proxy(self):
    #     self.cursor.execute("SELECT ip FROM proxies ORDER BY RAND() LIMIT 1")
    #     result = self.cursor.fetchone()
    #     if result:
    #         return result[0]
    #
    # def process_request(self, request, spider):
    #     proxy_address = self.get_random_proxy()
    #     if proxy_address:
    #         print("使用代理:", proxy_address)
    #         request.meta['proxy'] = f'http://{proxy_address}'


    # ========================在settings.py中设置代理池和cookie池=====================
    # def __init__(self, proxies, cookies):
    #     self.proxies = proxies
    #     self.cookies = cookies
    #
    # @classmethod
    # def from_crawler(cls, crawler):
    #     # 从 settings 中获取 PROXY_LIST 和 COOKIE_LIST
    #     proxies = crawler.settings.get('PROXY_LIST')
    #     cookies = crawler.settings.get('COOKIE_LIST')
    #
    #     # 配置检查
    #     if not proxies or not cookies:
    #         raise NotConfigured
    #
    #     # 创建并返回 MyMiddleware 的实例
    #     return cls(proxies=proxies, cookies=cookies)

    # ========================在settings.py中设置代理池=====================
    def __init__(self, proxies):
        self.proxies = proxies

    @classmethod
    def from_crawler(cls, crawler):
        return cls(proxies=crawler.settings.get('PROXY_LIST'))

    def get_proxy(self):
        return choice(self.proxies)

    def process_request(self, request, spider):
        # 第一种不带用户名和密码的方式
        # request.meta['proxy'] = "http://ip:port"
        # 第二种带用户名和密码的方式
        # request.meta['proxy'] = "http://user:password@ip:port"
        # proxy_address = choice(self.proxies).strip()
        # print("使用代理:", proxy_address)
        # request.meta['proxy'] = proxy_address
        request.meta['proxy'] = self.get_proxy()

    def process_exception(self, request, exception, spider):
        if isinstance(exception, Exception):
            # 更换代理并重试
            self.change_proxy(request)
            return request

    def change_proxy(self, request):
        request.meta['proxy'] = self.get_proxy()
