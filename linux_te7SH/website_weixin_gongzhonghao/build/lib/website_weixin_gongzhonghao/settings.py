# Scrapy settings for website_weixin_gongzhonghao project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "website_weixin_gongzhonghao"

SPIDER_MODULES = ["website_weixin_gongzhonghao.spiders"]
NEWSPIDER_MODULE = "website_weixin_gongzhonghao.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
   "Accept-Language": "en",
   "Cookie": "Qs_lvt_323937=1730546101; Qs_pv_323937=1990824650526840600; _qpsvr_localtk=0.5182466392510181; RK=99MFyIJWGr; ptcz=276f30f6bbbde8781956bdbea3e63169b7925f32d01bd166a0e7ad02ea3e68f9; ua_id=UvE1QYKH4S0urZ3MAAAAAOTSYIczVbtcs-rAZ5uGcFg=; wxuin=30644573284447; _clck=1n57w1u|1|fql|0; uuid=4d0a6cab494bba18f5855a8e78585cab; rand_info=CAESIIKrndRuwK8Vnpah3oiTLfMGWHlSyKHg3P8EJbT52e8N; slave_bizuin=3938829078; data_bizuin=3938829078; bizuin=3938829078; data_ticket=cllPl6XZPbPlOUjeUjAKIhX2FemulGvYoPPwps0bmF9QX8JpBssZpiquQgwTwHFi; slave_sid=ZmFCbk1xUGdOVjdIUkJTaVFmb2dhelNPZUt0RkxpX2ZqZExCUkljQ0ppSkNFX0VlenR0ZUd6aGw2S3Badk1vV0FtRkVLNDRqelVrM0RJV094Y1R2bnRnNTBrdVpKSW1fbFFZNkduTlg1dUlwaE1JbFpzdFEydlVLMXVkZHNyUVFjSWtTeUtpcFJualBIOGIx; slave_user=gh_7915c60d6522; xid=cd0b778439d2c9072f607d3e86006c69; mm_lang=zh_CN; _clsk=1ux11jn|1730692737201|3|1|mp.weixin.qq.com/weheat-agent/payload/record"
}

WEIXING_TAKEN = '448756200'

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "website_weixin_gongzhonghao.middlewares.WebsiteWeixinGongzhonghaoSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "website_weixin_gongzhonghao.middlewares.WebsiteWeixinGongzhonghaoDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html

ITEM_PIPELINES = {
   "website_weixin_gongzhonghao.pipelines.WebsiteWeixinGongzhonghaoPipeline": 300,
   # "scrapyelasticsearch.scrapyelasticsearch.ElasticSearchPipeline": 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# settings.py
DATABASE = {
    'host': '127.0.0.1',  # 数据库主机地址
    'port': 3306,
    'user': 'public_sentiment',  # 数据库用户名
    'password': 'df32KX2fseEaPANK',  # 数据库密码
    'database': 'public_sentiment'  # 数据库名称
}

ELASTICSEARCH_DATABASE = {
    'host': '127.0.0.1',  # es主机地址
    'port': 9200,
    'user': 'elastic',  # es用户名
    'password': 'KP*rb=PlOgQejHaYIB0P',  # es密码
    'database': 'my_scrapy_index'  # 索引名称
}

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
