# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SephoracrawlerItem(scrapy.Item):
    ingredients = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    category = scrapy.Field()
    sub_category = scrapy.Field()
    url = scrapy.Field()
    brand = scrapy.Field()
    image = scrapy.Field()
    unsafe_ingredients = scrapy.Field()
    is_safe = scrapy.Field()
    love_count = scrapy.Field()
    detail = scrapy.Field()
