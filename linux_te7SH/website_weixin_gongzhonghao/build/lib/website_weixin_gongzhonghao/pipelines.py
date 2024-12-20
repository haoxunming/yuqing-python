# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import sys
import os
# 获取当前脚本所在目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 添加模块路径
sys.path.append(current_dir)
# import es_utils
import db_utils

from es_utils import insert_update_doc_by_url


class WebsiteWeixinGongzhonghaoPipeline:
    def process_item(self, item, spider):
        # es_utils.insert_update_doc_by_url(item)
        db_utils.insert_one(item)
        return item
