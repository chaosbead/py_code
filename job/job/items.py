# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JobItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    post = scrapy.Field()
    href = scrapy.Field()
    company = scrapy.Field()
    city = scrapy.Field()
    salary = scrapy.Field()
    min_salary = scrapy.Field()
    max_salary = scrapy.Field()
    publish_date = scrapy.Field()
