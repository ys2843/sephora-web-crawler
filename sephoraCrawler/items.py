# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SephoracrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    category = scrapy.Field()
    sub_category = scrapy.Field()
    affiliate_link = scrapy.Field()
    website = scrapy.Field()
    brand = scrapy.Field()
    images = scrapy.Field()
    image_urls = scrapy.Field()
