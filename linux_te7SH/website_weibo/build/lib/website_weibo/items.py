# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WebsiteWeiboItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class WeiboItem(scrapy.Item):
    # 来源平台
    type_str = scrapy.Field()
    # 标题
    title = scrapy.Field()
    # 作者
    author = scrapy.Field()
    # 关键词
    keywords = scrapy.Field()
    # 发布地区
    pulish_region = scrapy.Field()
    # 发布时间
    date = scrapy.Field()
    date_str = scrapy.Field()
    # 内容
    content = scrapy.Field()
    # 链接
    url = scrapy.Field()
    # 来源
    source = scrapy.Field()
    # 转发数
    reposts_count = scrapy.Field()
    # 评论数
    comments_count = scrapy.Field()
    # 点赞数
    attitudes_count = scrapy.Field()
    # 收藏数
    collects_count = scrapy.Field()
    # 来源平台
    source_platform = scrapy.Field()
    # 原文链接
    qriginal_link = scrapy.Field()
    # 情感分析
    snowNLP_anay = scrapy.Field()
    # 情感类型
    emotion_type = scrapy.Field()
