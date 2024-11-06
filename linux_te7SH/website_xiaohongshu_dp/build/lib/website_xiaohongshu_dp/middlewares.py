# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import time
import random
from scrapy import signals
from DrissionPage import ChromiumPage
from urllib.parse import urljoin

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class WebsiteDrissionPageMiddleware:
    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        url = request.url
        dirver = spider.driver  # 获取在爬虫类中定义的浏览器对象
        self.list_data = []
        if url in spider.list_data_link:
            dirver.get(f'{url}')
            for i in range(1, 3):
                self.get_info(dirver, i)
                self.page_scroll_down(dirver)

        print(self.list_data)

    def page_scroll_down(self, dirver):
        print(f"********下滑页面********")
        dirver.scroll.to_bottom()
        # 生成一个1-2秒随机时间
        random_time = random.uniform(1, 2)
        # 暂停
        time.sleep(random_time)

    def get_info(self, page, i):
        base_url = "https://www.xiaohongshu.com"
        # 定位包含笔记信息的sections
        container = page.ele('.feeds-container')
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

            print(f"第{i}页笔记：{note_type}，{title}")
            # 作者
            author_wrapper = footer.ele('.author-wrapper')
            # 作者
            author = author_wrapper.ele('.name', timeout=0).text

            self.list_data.append([note_type, title, author, complete_note_link])



class WebsiteXiaohongshuDpSpiderMiddleware:
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


class WebsiteXiaohongshuDpDownloaderMiddleware:
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
