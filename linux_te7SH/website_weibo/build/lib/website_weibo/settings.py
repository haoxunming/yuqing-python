# Scrapy settings for website_weibo project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "website_weibo"

SPIDER_MODULES = ["website_weibo.spiders"]
NEWSPIDER_MODULE = "website_weibo.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.1.2 Safari/537.36 JiSu/118.0.1.2"

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
# 第一种：不启动
# 第二种：启动，不开启（False）,默认使用DEFAULT_REQUEST_HEADERS中配置的cookie
# 第三种：启动，开启（True）,不常用
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
   "Accept-Language": "en",
   "cookie":"XSRF-TOKEN=t26JPiEXd5VoWIulGhBIzqUJ; PC_TOKEN=71b0e1b6c0; SCF=AvfWjWIxTohK-43P02hsfqzkOOhWF1b6dgo7MLZk3584_KOSTTA648sdrBf5GP-_1FDGQiy_5uFnTeEme6Wnb2w.; SUB=_2A25KI_jjDeRhGeNH4lYX9SrOyDSIHXVpQXQrrDV8PUNbmtAbLUj8kW9NSnXbHKCcdiLDoMlB9-N2An1nHGzzM2B-; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWfFaapTAxvjd0YoqRQ688E5JpX5KzhUgL.Fo-41KBcSKBEe0n2dJLoI7H9Ig90P7tt; ALF=02_1733236147; WBPSESS=CiQETiCir9LgF9MfEU_Ia-g6Y6CVMdQvXrfuDq2q0kzlZZsZFZWouekXbk7boB3H8a972n5pxM1uxwr4zDqdwMm6mFxvif_OvK1lp-6nvaN9DUxM2GNQtPNhVB0SWTueNAYvCVIB0ccim1okv1o9AA=="
   # "cookie":"XSRF-TOKEN=kF_60Sc001obYAxq6LSQt71F; _s_tentry=weibo.com; Apache=8719627060915.036.1722749140849; SINAGLOBAL=8719627060915.036.1722749140849; ULV=1722749140907:1:1:1:8719627060915.036.1722749140849:; SCF=AnDDMAqPdzLbELGStRgh8acmw0b7vWaqTc7PgkehCypTG7kWwvAIcvsq32Ydul2a-1fNJ6em6rGy_oVeTUL1LpA.; appkey=; WBtopGlobal_register_version=2024080414; PC_TOKEN=c4088dde9a; SUB=_2A25Lq1reDeRhGeBG61AR9ybIzzWIHXVoydIWrDV8PUNbmtAGLWb9kW9NRj7nmS4wLNtS56HJNjntUkyb0jSLM5gG; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhCxr0koNwZDE0vCwJcauIx5JpX5KzhUgL.FoqRehz7S0nXSh.2dJLoIp-LxKBLB.2L1K2LxKqLBoqL12epeh2t; ALF=02_1725347725; WBPSESS=Dt2hbAUaXfkVprjyrAZT_DpWNPgdT4rjmNpWXVuxVXsTSbHiIMAQRokGDZ5qMwixgQ2J621gxqtKKumd1fZqFJClVIoFmIpat2gSHo9fnBt42n0FwZ6mIzXceptVjZa1-lL0Ad1RNy0dEMXeiZK9C5znMf9KtdYKVcwjgwXBX9-H9Q6Zjwv8EkIN5Q4j_MIT3UiwJsGcGBobRLBzh3daQw=="
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "website_weibo.middlewares.WebsiteWeiboSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    "website_weibo.middlewares.WebsiteWeiboDownloaderMiddleware": 543,
#    "website_weibo.middlewares.ProxyMiddleware": 543,
#    "scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware": 110,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "website_weibo.pipelines.WebsiteWeiboPipeline": 300,
    # "scrapyelasticsearch.scrapyelasticsearch.ElasticSearchPipeline": 300,
}

# 设置代理列表
PROXY_LIST = [
    'https://117.50.108.90:7890',
    'http://39.107.33.254:8090',
    'http://139.9.119.20:80',
]

# Elasticsearch配置
# Elasticsearch server configuration
# ELASTICSEARCH_SERVERS = ['https://192.168.10.20:9200']
ELASTICSEARCH_SERVERS = ['https://47.94.246.151:9200']
# ELASTICSEARCH_PORT = 9200

# Optional: Elasticsearch scheme (http or https)
# ELASTICSEARCH_SCHEME = 'https'

# Optional: Elasticsearch index name
ELASTICSEARCH_INDEX = 'my_scrapy_index'

ELASTICSEARCH_USERNAME = 'elastic'
#ELASTICSEARCH_PASSWORD = 'UveEiPJCSOgBfChzHkZN'
ELASTICSEARCH_PASSWORD = '+3*cj2yW=oyZBlfcpFVb'

# Optional: Elasticsearch index settings
# ELASTICSEARCH_INDEX_SETTINGS = {
#    'number_of_shards': 1,
#    'number_of_replicas': 0,
# }
# ELASTICSEARCH_CA = {
#    "CA_CERT": "C:\\Users\\16321\\.conda\\envs\\collection_project\\Lib\\site-packages\\scrapyelasticsearch\\ca.pem",
#    "CLIENT_KEY": "C:\\Users\\16321\\.conda\\envs\\collection_project\\Lib\\site-packages\\scrapyelasticsearch\\client.key",
#    "CLIENT_CERT": "C:\\Users\\16321\\.conda\\envs\\collection_project\\Lib\\site-packages\\scrapyelasticsearch\\client.crt"
# }
ELASTICSEARCH_CA = {
   "CA_CERT": False,
   "VERIFY_CERTS": False
}
# Optional: Elasticsearch type name
ELASTICSEARCH_TYPE = 'scrapy_items'

ELASTICSEARCH_UNIQ_KEY = 'qriginal_link'

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
