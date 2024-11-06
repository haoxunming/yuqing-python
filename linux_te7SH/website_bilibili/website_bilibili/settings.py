# Scrapy settings for website_bilibili project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "website_bilibili"

SPIDER_MODULES = ["website_bilibili.spiders"]
NEWSPIDER_MODULE = "website_bilibili.spiders"


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
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
   "Accept-Language": "en",
   "Cookie": "buvid3=7CB0D253-6AAC-3D53-B68B-5B157A13987132971infoc; b_nut=1729923832; _uuid=7C657BBC-72C8-3211-A3BC-107AB9C810AA1334438infoc; buvid4=0FB2A54B-C42A-69F6-7C28-8ADB94A416D572234-024102404-MsNJcCXGRnTVTSTC6C4wiA%3D%3D; buvid_fp=0a091939f44076442ddf5abdd30be849; b_lsid=98DAF137_192F270CB9B; header_theme_version=CLOSE; enable_web_push=DISABLE; SESSDATA=1916bbdb%2C1746196369%2Cea884%2Ab2CjDA-3JJeBZjB-D6LDvfWzmi1NnjHWC3xJiJqvdOoIcASU0YPFd9vt1OG0W3FyK-HFwSVnRZUlVoV0hzTk1kT2cxa3lBX0pEek5heEh3SHFWa3VETkF0ZkdJR0tQenp0WkRkN1dWb1BSRUZpbUNwNlgxdHBjdkV0bzBLaDN6SDFBckhZQmpvaF93IIEC; bili_jct=e6540b2e08dca2a659786397849ac433; DedeUserID=293802310; DedeUserID__ckMd5=5e1a5acad5a865a0; sid=h6deg4jv; home_feed_column=4; browser_resolution=977-1146"
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

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "website_bilibili.middlewares.WebsiteBilibiliSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "website_bilibili.middlewares.WebsiteBilibiliDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   "website_bilibili.pipelines.WebsiteBilibiliPipeline": 300,
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
