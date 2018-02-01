# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from scrapy.conf import settings
from scrapy.exceptions import DropItem
from scrapy import log


class SephoracrawlerPipeline(object):
    def __init__(self):
        collection = pymongo.MongoClient(
            settings['MONGO_SERVER'],
            settings['MONGO_PORT']
        )
        self.db = collection[settings['MONGO_DB']]
        self.collection = self.db[settings['MONGO_COLL']]

    def process_item(self, item, spider):
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        if valid:
            self.collection.insert(dict(item))
            log.msg("Product added to MongoDB database!",
                    level=log.DEBUG, spider=spider)
        return item

