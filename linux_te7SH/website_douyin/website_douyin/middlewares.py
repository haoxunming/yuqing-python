# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

import requests
import random
import time
from bs4 import BeautifulSoup

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class ProxyPool:
    def __init__(self, test_url='http://httpbin.org/ip', timeout=5):
        self.proxies = []
        self.test_url = test_url
        self.timeout = timeout

    # 许多公开代理网站会定期提供免费的代理IP列表，如：
    #
    # free-proxy-list.net ： https://free-proxy-list.net/
    # sslproxies.org ： https://www.sslproxies.org/
    # us-proxy.org： https://www.us-proxy.org/
    # 这些网站一般会提供HTTP和HTTPS代理的IP地址和端口号。你可以编写一个爬虫定期抓取这些网站来更新代理池。

    # 以下以以抓取free-proxy-list.net 为例，我们可以抓取其中的代理 IP 和端口信息。
    def fetch_proxies_from_free_proxy_list(self):
        url = 'https://free-proxy-list.net/'
        response = requests.get(url)

        # 解析 HTML 内容
        soup = BeautifulSoup(response.text, 'html.parser')
        proxy_list = []

        # 查找代理表格中的代理信息
        table = soup.find('table', id='proxylisttable')
        for row in table.tbody.find_all('tr'):
            columns = row.find_all('td')
            ip = columns[0].text
            port = columns[1].text
            https = columns[6].text

            # 只选择支持 HTTPS 的代理
            if https == 'yes':
                proxy = f"https://{ip}:{port}"
                proxy_list.append(proxy)

        return proxy_list

    # 获取免费的代理IP列表，如：地址： https://www.zdaye.com/free/beijing_ip.html
    def fetch_proxies_from_free_proxy_list_240917(self):
        url = 'https://www.zdaye.com/free/beijing_ip.html'
        response = requests.get(url)

        # 解析 HTML 内容
        soup = BeautifulSoup(response.text, 'html.parser')
        proxy_list = []

        # 查找代理表格中的代理信息
        table = soup.find('table', id='proxylisttable')
        for row in table.tbody.find_all('tr'):
            columns = row.find_all('td')
            ip = columns[0].text
            port = columns[1].text
            https = columns[6].text

            # 只选择支持 HTTPS 的代理
            if https == 'yes':
                proxy = f"https://{ip}:{port}"
                proxy_list.append(proxy)

        return proxy_list

    # 一些第三方代理服务商提供API，允许你通过API请求动态获取代理IP。常见的第三方代理服务包括：
    # ProxyMesh：提供按需获取的 HTTP代理API
    # BrightData（原Luminati）：一个大型的付费代理服务平台
    # Crawlera：Scrapy官方提供的代理管理服务。
    # 这些服务通常要求你注册并获取API密钥。你可以使用API来获取代理。
    def fetch_proxies_from_api(self):
        api_url = 'https://api.proxy-provider.com/get_proxy'
        api_key = 'your_api_key'  # 替换为你的 API 密钥

        params = {
            'api_key': api_key,
            'count': 5  # 获取5个代理
        }

        response = requests.get(api_url, params=params)

        if response.status_code == 200:
            proxies = response.json().get('proxies', [])
            proxy_list = []

            for proxy in proxies:
                protocol = 'https' if proxy.get('https', False) else 'http'
                proxy_url = f"{protocol}://{proxy['ip']}:{proxy['port']}"
                proxy_list.append(proxy_url)

            return proxy_list
        else:
            print(f"Failed to fetch proxies, status code: {response.status_code}")
            return []
    def update_proxies(self):
        # 从代理源获取代理（可以从第三方 API 或爬取的公开代理网站）
        new_proxies = self.fetch_proxies_from_source()
        self.proxies.extend(new_proxies)
        self.filter_valid_proxies()

    def fetch_proxies_from_source(self):
        # 模拟从公开代理网站或者第三方 API 获取代理
        # 这里你可以用爬虫或 API 获取代理列表
        return [
            'http://123.456.789.001:8000',
            'http://234.567.890.123:8000',
            'http://345.678.901.234:8000'
        ]

    def fetch_proxies_from_source(self):
        # 从代理网站和第三方 API 获取代理
        proxies = self.fetch_proxies_from_free_proxy_list()  # 从网站获取代理
        proxies += self.fetch_proxies_from_api()  # 从 API 获取代理
        return proxies

    def filter_valid_proxies(self):
        # 测试代理是否可用，保留有效代理
        valid_proxies = []
        for proxy in self.proxies:
            if self.is_proxy_valid(proxy):
                valid_proxies.append(proxy)

        # 更新代理池，保留有效的代理
        self.proxies = valid_proxies

    def is_proxy_valid(self, proxy):
        try:
            # 测试代理的有效性（发起测试请求）
            response = requests.get(self.test_url, proxies={"http": proxy, "https": proxy}, timeout=self.timeout)
            if response.status_code == 200:
                return True
        except Exception:
            return False
        return False

    def get_random_proxy(self):
        # 从有效代理中随机返回一个
        if not self.proxies:
            self.update_proxies()  # 如果没有可用代理，更新代理池
        return random.choice(self.proxies)

    def clean_pool(self):
        # 定期清理代理池中过时的代理
        self.filter_valid_proxies()

    def run(self, update_interval=300):
        # 每隔一段时间（例如300秒）更新代理池
        while True:
            self.update_proxies()
            print(f"Updated proxy pool: {self.proxies}")
            time.sleep(update_interval)

class ProxyMiddleware:
    def __init__(self):
        self.proxy_pool = ProxyPool()

    def process_request(self, request, spider):
        # 获取随机可用代理
        proxy = self.proxy_pool.get_random_proxy()
        if proxy:
            request.meta['proxy'] = proxy
            spider.logger.info(f'Using proxy: {proxy}')


class CustomUserAgentMiddleware:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
            'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36'
        ]

    def process_request(self, request, spider):
        request.headers['User-Agent'] = random.choice(self.user_agents)

class WebsiteDouyinSpiderMiddleware:
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


class WebsiteDouyinDownloaderMiddleware:
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
