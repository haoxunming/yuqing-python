# Scrapy settings for website_douyin project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "website_douyin"

SPIDER_MODULES = ["website_douyin.spiders"]
NEWSPIDER_MODULE = "website_douyin.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

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
   "Accept": "application/json, text/plain, */*",
   "Accept-Language": "en",
   "cookie": "__ac_signature=_02B4Z6wo00f01.4UtmgAAIDDyTByNPWQw9f-NLLAAJiq45; ttwid=1%7CCQSNV54LE0nodNv955saqpY1B9oMkYBWQqNmZYav9KQ%7C1730421647%7Cc4bededd6ebfa00adae7a6675e8fa3d9a9f8e932a257ac607edc12a59ab36a0b; UIFID_TEMP=63bdc4b4b456901f349a081bfd3a24da10a1c6623f0a2d5eadd83f51c9f4d11228dfe5a52bddc6878fbd5efd7c7cdec3f653738ebb717b72563a32a954bb8a4e64d6e7e801d23801637923897677c3ac; s_v_web_id=verify_m2y0deah_oSN9r83h_Zfac_47s4_Av7Y_avJdDQuWWILO; hevc_supported=true; dy_swidth=3440; dy_sheight=1440; csrf_session_id=b078529335edcb775591d7546a032d6b; fpk1=U2FsdGVkX19NFnGqZe9zkCAomwu9WTPMMJJXCzukUAeVB1ahKrHysXygslvLHW63H4lwCW9EYJUKJC6Wr+Unmg==; fpk2=7675d59b5e84e0a878ee6f0a97f9056f; passport_csrf_token=cffc075d526d13ecdaa0305370f92dac; passport_csrf_token_default=cffc075d526d13ecdaa0305370f92dac; bd_ticket_guard_client_web_domain=2; FORCE_LOGIN=%7B%22videoConsumedRemainSeconds%22%3A180%7D; UIFID=63bdc4b4b456901f349a081bfd3a24da10a1c6623f0a2d5eadd83f51c9f4d11228dfe5a52bddc6878fbd5efd7c7cdec3c88dddbd1aa980062c28fdd7bf0ec6bc21fbd2269a2c921bdf4c3b95cdc368f21981297689713e1bbb1f8984e37f01924ee6383a662c4c1ab61b540bb473b0d489ee7f2e554af3ddf603d6dfe6b8130a7d574f80daf6c85ce121a622d799d301c65e6861f3b3feb739e00c5c01e6ea85; douyin.com; device_web_cpu_core=20; device_web_memory_size=8; architecture=amd64; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A3440%2C%5C%22screen_height%5C%22%3A1440%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A20%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22; strategyABtestKey=%221730644203.495%22; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Atrue%2C%22volume%22%3A0.162%7D; xgplayer_user_id=25266614630; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCQ21NcWI5OWFNR3hVdmhxVTAwQWRTZHBQV1dIdG9ROCtSS29NcVpoczV6ZzVBREk5TWYzdzFXVUpPbUxKbVdhVlNBWkpRLzgwMXZ5Z2F2RmUxRWgwekk9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoyfQ%3D%3D; biz_trace_id=882b939a; sdk_source_info=7e276470716a68645a606960273f276364697660272927676c715a6d6069756077273f2771777060272927666d776a68605a607d71606b766c6a6b5a7666776c7571273f275e5927666d776a686028607d71606b766c6a6b3f2a2a6c676163606c686e6269666861606f757564676e646c61756c75756b6c6c6a672a666a6b71606b712a76716477715a7666776c75714770762b6f765927295927666d776a686028607d71606b766c6a6b3f2a2a6c676163606c686e6269666861606f757564676e646c61756c75756b6c6c6a672a666a6b71606b712a7666776c75714770762b6f76592758272927666a6b766a69605a696c6061273f27636469766027292762696a6764695a7364776c6467696076273f275e5827292771273f2734313030353731313335363234272927676c715a75776a716a666a69273f2763646976602778; bit_env=WB2mQe7jm-FBCfKo7HJnxQPp0bRL18l_RxJZbVMv5Yz_eDDqBMVpb-6slCU4m4LPcQDpMCBEo7zmJ5B7B_RC6dJNXrUUBR-D4aIV8OdOE0KsHtEdE8zjGtJs_Foh2HmsxSHPcfthziD17dDjHChlFbVVv4dvXkJW8d7wmRFGkegzsrSdW0llkTQQWeVnAvw7iyEXlOHgjNIYVKYVZoMEWgj6GurC74XBZOJG39cC2GgMroyprAzAKXLh7hpo9-NoOZqAlAIfg8vKZWGNeH_0Ach4bfrLmhDxmQPIB2xkYoNWD0e_YCzfDNzt-LHSiuQ_WZX0sH6oo9vaVo4S6bb4Rfms7oMslDgpJ-qE6G9z0X96MLQWEZuxyaWSlKXx2j4axmoWB5C5sk5t_aBPHDWM0ZYNZc7PwOJfKtdj_mxlejHgGSGpHvE1pZvPVvL--Qm4_LnYpNtllngiW0g0aDGsHItaFwaq-TNEc0e_JRlW_Y_G-LVAZfcH6RiRgHLH-2_l; gulu_source_res=eyJwX2luIjoiZDg4YmU1YzYyOTY3MTM3ZmE5OWY4N2MxMzRlYmZlNmU2YWY4YWQzNWI0MzQ5OGVhNTYzOThiMDAxNjYwODYxYyJ9; passport_auth_mix_state=vbxrns5ubefhyh7ps2omlzv3f6ylep1n; passport_assist_user=CkHME_wcJ9Au8yb1oFoZqQ8o40vty3xKmGctZhNN4snNQl0B4ej_QUMBq_aEEQ7RfOwLHSe9uJHdj7Lgi6eqPq_OfxpKCjynBSDAzeyFzQAAWXkDoIWGXc6utgxwBo8NhxsJL1ex5hi8DM_cVDaUJlZ1XVUWTdlDoSUFOv0upXe3R0sQ-L_gDRiJr9ZUIAEiAQMtfqhW; n_mh=EXYlCtoC_XliiRkUy8yXN7WegU5DjrbBR3aL3Rx05Ys; sso_uid_tt=1b681fd5ff13599eb65273708efda0c5; sso_uid_tt_ss=1b681fd5ff13599eb65273708efda0c5; toutiao_sso_user=92f4f11a1518ad586be69ae4de459216; toutiao_sso_user_ss=92f4f11a1518ad586be69ae4de459216; sid_ucp_sso_v1=1.0.0-KGNhYzdjNDMxNDdkYmUwNjhkZWU4NmY2MzI5NTc5M2Y0ZGE2NDg2ZGIKIQjA_vCkjo3VAhCJkp65BhjvMSAMMKSVuZQGOAZA9AdIBhoCaGwiIDkyZjRmMTFhMTUxOGFkNTg2YmU2OWFlNGRlNDU5MjE2; ssid_ucp_sso_v1=1.0.0-KGNhYzdjNDMxNDdkYmUwNjhkZWU4NmY2MzI5NTc5M2Y0ZGE2NDg2ZGIKIQjA_vCkjo3VAhCJkp65BhjvMSAMMKSVuZQGOAZA9AdIBhoCaGwiIDkyZjRmMTFhMTUxOGFkNTg2YmU2OWFlNGRlNDU5MjE2; download_guide=%221%2F20241103%2F0%22; login_time=1730644234830; passport_auth_status=2857db201ff2fa63e41e2910adae33c4%2C; passport_auth_status_ss=2857db201ff2fa63e41e2910adae33c4%2C; uid_tt=650124e6bd52cbf94c45e0c1f3c2de3f; uid_tt_ss=650124e6bd52cbf94c45e0c1f3c2de3f; sid_tt=d839fbad21f12252a3d18c4623a4b775; sessionid=d839fbad21f12252a3d18c4623a4b775; sessionid_ss=d839fbad21f12252a3d18c4623a4b775; is_staff_user=false; __ac_nonce=06727890a004bf5c3113a; publish_badge_show_info=%220%2C0%2C0%2C1730644235637%22; _bd_ticket_crypt_doamin=2; _bd_ticket_crypt_cookie=a06b13f4dce54bb5c3967d998c80a17d; SelfTabRedDotControl=%5B%7B%22id%22%3A%227309107288260741147%22%2C%22u%22%3A178%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227269017433883543608%22%2C%22u%22%3A127%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227161587433551693860%22%2C%22u%22%3A17%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227207825437051848763%22%2C%22u%22%3A67%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227086885489000581127%22%2C%22u%22%3A23%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227337212556916590629%22%2C%22u%22%3A35%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227166326638911686671%22%2C%22u%22%3A69%2C%22c%22%3A0%7D%2C%7B%22id%22%3A%227159196786551162894%22%2C%22u%22%3A109%2C%22c%22%3A0%7D%5D; __security_server_data_status=1; odin_tt=7a77f4f2a0b824da561b7bcf237425a691325ef8949b44ed57a302d15bff0b18d1ca56ce6e8094d4874d340cff901aa3; sid_guard=d839fbad21f12252a3d18c4623a4b775%7C1730644236%7C5184000%7CThu%2C+02-Jan-2025+14%3A30%3A36+GMT; sid_ucp_v1=1.0.0-KDA5ODc1YWMwZWI4NmVhMzQ3Yjg3MmE4MDQwODViMjQ0NThjMGJkZTIKGwjA_vCkjo3VAhCMkp65BhjvMSAMOAZA9AdIBBoCbHEiIGQ4MzlmYmFkMjFmMTIyNTJhM2QxOGM0NjIzYTRiNzc1; ssid_ucp_v1=1.0.0-KDA5ODc1YWMwZWI4NmVhMzQ3Yjg3MmE4MDQwODViMjQ0NThjMGJkZTIKGwjA_vCkjo3VAhCMkp65BhjvMSAMOAZA9AdIBBoCbHEiIGQ4MzlmYmFkMjFmMTIyNTJhM2QxOGM0NjIzYTRiNzc1; WallpaperGuide=%7B%22showTime%22%3A0%2C%22closeTime%22%3A0%2C%22showCount%22%3A0%2C%22cursor1%22%3A10%2C%22cursor2%22%3A2%7D; passport_fe_beating_status=false; xg_device_score=7.818598560905933; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A1%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A0%7D%22; IsDouyinActive=true; home_can_add_dy_2_desktop=%220%22"
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "website_douyin.middlewares.WebsiteDouyinSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "website_douyin.middlewares.WebsiteDouyinDownloaderMiddleware": 543,
#}

# scrapy-user-agents 是一个现成的插件，可以轻松在 Scrapy 项目中实现随机化 User-Agent 的功能。首先需要安装此插件：
# pip install scrapy-user-agents

# DOWNLOADER_MIDDLEWARES = {
#    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,  # 禁用默认的 UserAgentMiddleware
#    'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,      # 启用随机 User-Agent 中间件
#    'website_douyin.middlewares.CustomUserAgentMiddleware': 543,  # 自定义 User-Agent 中间件
# }


# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   "website_douyin.pipelines.WebsiteDouyinPipeline": 300,
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
