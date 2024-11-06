# Scrapy settings for website_wangyi project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "website_wangyi"

SPIDER_MODULES = ["website_wangyi.spiders"]
NEWSPIDER_MODULE = "website_wangyi.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.1.2 Safari/537.36 JiSu/118.0.1.2"

USER_AGENTS = {
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.1.2 Safari/537.36 JiSu/118.0.1.2",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0"
}
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
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "website_wangyi.middlewares.WebsiteWangyiSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "website_wangyi.middlewares.WebsiteWangyiDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   "website_wangyi.pipelines.WebsiteWangyiPipeline": 300,
   # "scrapyelasticsearch.scrapyelasticsearch.ElasticSearchPipeline": 300,
}

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

# Optional: Elasticsearch base to use for item scraped signal
# ELASTICSEARCH_SIGNAL_BASE = 'elasticsearch'

# Optional: use Elasticsearch as spider metadata storage
# ELASTICSEARCH_UNIQUIFIER = 'hash'
# 如果Elasticsearch需要认证，可以在Elasticsearch客户端构造函数中添加认证参数

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

DATABASE = {
    'host': '127.0.0.1',  # 数据库主机地址
    'port': 3306,
    'user': 'public_sentiment',  # 数据库用户名
    'password': 'df32KX2fseEaPANK',  #  数据库密码
    'database': 'public_sentiment',  #数据库名称
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
