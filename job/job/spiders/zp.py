# -*- coding: utf-8 -*-
import scrapy
from job.items import JobItem

class ZpSpider(scrapy.Spider):
    name = 'zp'
    allowed_domains = ['51job.com']
    url = 'https://search.51job.com/list/000000,000000,0000,00,9,99,%25E6%2595%25B0%25E6%258D%25AE%25E5%2588%2586%25E6%259E%2590%25E5%25B8%2588,2,1.html'
    start_urls = [url]


    def extract_with_xpath(self,tag,path):
        result = tag.xpath(path).extract_first()
        if result:
            return result.strip()
        else:
            return ''

    def parse(self, response):
        zw_div = response.xpath('//div[@class="el"]')

        for item in zw_div:
            item_1 = JobItem()

            item_1['post'] = self.extract_with_xpath(item,'p/span/a/@title')
            item_1['company'] = self.extract_with_xpath(item,'span[@class="t2"]/a/text()')
            item_1['city'] = self.extract_with_xpath(item,'span[@class="t3"]/text()')
            item_1['salary'] = self.extract_with_xpath(item,'span[@class="t4"]/text()')
            item_1['publish_date'] = self.extract_with_xpath(item,'span[@class="t5"]/text()')
            item_1['href'] = self.extract_with_xpath(item,'p[@class="t1 "]/span/a/@href')

            yield item_1

            #分页   //div[@class="dw_page"]//ul/li[last()]/a/@href
        for next_page in response.xpath('//li[@class="bk"][2]/a/@href'):
            yield response.follow(next_page,self.parse)